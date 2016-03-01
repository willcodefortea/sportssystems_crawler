import csv
from .spider import SportSystemResultsSpider
from . import parser


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

    spider = SportSystemResultsSpider(event_id=event_id, callback=callback)
    spider.go()
