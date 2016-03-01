import csv
import datetime

from .spider import SportSystemResultsSpider
from . import parser
from .stats import Result


def build(event_id, out):
    """Fetch the data and write it to the given stream.

    :arg int event_id: The event ID we're interested in.
    :arg file out: A file like object to write our CSV to.
    """
    writer = csv.DictWriter(
        out,
        fieldnames=[
            'pos', 'time', 'name', 'team', 'cat', 'num', 'chip', 'grade',
        ],
        delimiter='\t',
        extrasaction='ignore'
    )
    writer.writeheader()

    # Create a closure with out CSV writer as our callback
    def callback(result):
        for cell in parser.parse(result.content):
            writer.writerow(cell)
        # As this callback runs in a distinct thread, flush the stream
        # now
        out.flush()

    spider = SportSystemResultsSpider(event_id=event_id, callback=callback)
    spider.go()


def build_results(fin):
    """Build a sorted result set from an input stream."""
    reader = csv.reader(fin, delimiter='\t')
    results = []

    for row in reader:
        if row[0] == 'pos':
            # Header row, skip it
            continue
        hour, mins, seconds = [int(chunk) for chunk in row[1].split(':')]

        results.append(Result(
            time=datetime.time(hour, mins, seconds),
            name=row[2],
        ))

    results.sort(key=lambda item: item.time)
    return results
