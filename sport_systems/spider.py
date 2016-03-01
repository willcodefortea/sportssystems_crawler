import csv
import contextlib
import multiprocessing
import urllib

import requests
from . import parser


class Spider(object):
    """A simple spider to fetch URLS.

    :arg callable callback: A method that accepts a single argument
        (the response object) to be called whenever a request is
        completed.
    :arg int N: The number of processes to spawn. Defaults to double the
        number of available CPUs - 1 as one process is used for
        callbacks.
    :arg int max_retry: The number of times to attempt fetch a URL if an
        error response is returned.
    """
    def __init__(self, callback, N=None, max_retry=3):
        self.N = N if N else (multiprocessing.cpu_count() * 2 - 1)

        self.callback = callback

        self.url_queue = multiprocessing.JoinableQueue()
        self.results_queue = multiprocessing.JoinableQueue()
        self.errors_queue = multiprocessing.Queue()

        self.download_processes = []
        self.callback_process = multiprocessing.Process(
            target=self._callback,
            args=(self.results_queue, )
        )

        for _ in range(self.N):
            proc = multiprocessing.Process(
                target=self.download,
                args=(self.url_queue, self.results_queue, self.errors_queue)
            )
            proc.daemon = True
            self.download_processes.append(proc)

    def download(self, url_queue, results_queue, error_queue):
        """Perform a HTTP request.

        This method aims to be as ignorant of the implementation as
        possible, once a non error result has been downloaded, we push
        the result into a queue for the concrete class instance to do
        whatever it likes.
        """
        while True:
            data = url_queue.get()

            if not isinstance(data, str):
                url, try_count = data
            else:
                url, try_count = data, 0

            response = requests.get(url)

            if response.ok:
                results_queue.put(response)
            else:
                if try_count >= self.max_retry:
                    error_queue.put(response)
                else:
                    url_queue.put((url, try_count + 1))

            url_queue.task_done()

    def _callback(self, queue):
        """Private method to proxy a friendlier public callback.

        Rather than rely on subclasses to each mark tasks as done, we
        handle that here and simply provide an interface to handle the
        resulting content.
        """
        while True:
            result = queue.get()
            self.callback(result)
            queue.task_done()

    @contextlib.contextmanager
    def _process_manager(self):
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
        with self._process_manager():
            self.populate_urls()

            # Wait for all the items in the queue to be consumed
            self.url_queue.join()
            self.results_queue.join()

    def populate_urls(self):
        """Create URLs for this spider to fetch."""
        raise NotImplementedError()

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


class SportSystemResultsSpider(Spider):
    """A spider to crawl results from SportSystems."""

    #: The query endpoint for the result data.
    BASE_URL = 'http://www.sportsystems.co.uk/ss/results/data/{event_id}/'

    def __init__(self, event_id, page_size=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.event_id = event_id
        self.page_size = page_size

    def populate_urls(self):
        """Create URLs for this spider to fetch."""
        lim = -(-self.total_count // self.page_size)

        for page_num in range(1, lim + 1):
            url = self.build_url(page_num, count=self.page_size)
            self.url_queue.put(url)

    def build_url(self, page_num, link='N', posStart=None, count=20):
        """Build a URL for the specified page number.

        :arg int page_num: The page to fetch.
        :arg str link: The API will automatically generate a link to
            the runner's profile unless told not to.
        :arg int posStart: The offset within the results to start the
            page. (Defaults to the correct position for the given page.)
        :arg int count: The page size to return.
        """
        base_url = self.BASE_URL.format(event_id=self.event_id)

        params = {}

        params['link'] = link
        params['posStart'] = posStart or (page_num - 1) * count
        params['count'] = count

        querystring = urllib.parse.urlencode(params)
        return '%s?%s' % (base_url, querystring)

    @property
    def total_count(self):
        """The total number of results available."""
        if not hasattr(self, '_total_count'):
            self._total_count = self._fetch_total()
        return self._total_count

    def _fetch_total(self):
        """The total number of results for this event."""
        first_page_url = self.build_url(page_num=1, count=1)
        response = requests.get(first_page_url)

        if not response.ok:
            response.raise_for_status()

        return parser.extract_total(response.content)
