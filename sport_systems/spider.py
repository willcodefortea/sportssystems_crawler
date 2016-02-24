import csv
import contextlib
import multiprocessing

import requests
from . import parser


class Spider(object):
    """A simple spider to scrape results from SportSystems.

    :arg event_id: The event's ID that we're extracting data from.
    :arg N: The number of processes to spawn. Defaults to double the
        number of available CPUs - 1 as one process is used for
        callbacks.
    """
    PAGE_SIZE = 20

    def __init__(self, event_id, N=None):
        self.event_id = event_id
        self.N = N if N else (multiprocessing.cpu_count() * 2 - 1)

        self.url_queue = multiprocessing.JoinableQueue()
        self.results_queue = multiprocessing.JoinableQueue()

        self.download_processes = []
        self.callback_process = multiprocessing.Process(
            target=self.callback,
            args=(self.results_queue, )
        )

        for _ in range(self.N):
            proc = multiprocessing.Process(
                target=self.download,
                args=(self.url_queue, self.results_queue)
            )
            proc.daemon = True
            self.download_processes.append(proc)

        data_url = 'http://www.sportsystems.co.uk/ss/results/data/{}/'
        self.data_url = data_url.format(self.event_id)

    def download(self, page_queue, results_queue):
        """Perform a HTTP request and parse the reponse."""
        while True:
            page_num = page_queue.get()
            content = self._fetch_page(page_num, link='N')

            for result in parser.parse(content):
                results_queue.put(result)

            page_queue.task_done()

    def callback(self, queue):
        """Do something with data that's been retrieved."""
        while True:
            queue.get()
            queue.task_done()

    @contextlib.contextmanager
    def process_manager(self):
        """A simple context manager to clean up processes nicely."""
        for proc in self.download_processes:
            proc.start()
        self.callback_process.start()

        try:
            yield
        finally:
            # Our function has exited, shut down all running processes
            for proc in self.download_processes:
                proc.terminate()
            self.callback_process.terminate()

    def go(self):
        """Start all the things."""
        with self.process_manager():
            # Sneaky trick to round UP without casting
            lim = -(-self.total_count // self.PAGE_SIZE)

            for page_num in range(1, lim + 1):
                self.url_queue.put(page_num)

            # Wait for all the items in the queue to be consumed
            self.url_queue.join()
            self.results_queue.join()

    @property
    def total_count(self):
        """The total number of results available."""
        if not hasattr(self, '_total_count'):
            self._total_count = self._fetch_total()
        return self._total_count

    def _fetch_total(self):
        """The total number of results for this event."""
        content = self._fetch_page(page_num=1)
        return parser.extract_total(content)

    def _fetch_page(self, page_num=1, **params):
        params['posStart'] = (page_num - 1) * self.PAGE_SIZE
        params['count'] = self.PAGE_SIZE
        response = requests.get(self.data_url, params)

        if not response.ok:
            response.raise_for_status()

        return response.content


class CsvSpider(Spider):
    """Write output to a CSV as soon as results come in."""
    def __init__(self, out, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.out = out
        self.writer = csv.DictWriter(
            out,
            fieldnames=[
                'pos', 'time', 'name', 'team', 'cat', 'num', 'chip', 'grade',
            ],
            delimiter='\t',
            extrasaction='ignore'
        )
        self.writer.writeheader()

    def callback(self, queue):
        """Do something with data that's sent through the pipe."""
        while True:
            result = queue.get()
            self.writer.writerow(result)
            queue.task_done()
