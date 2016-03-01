
import os
import sys
from sport_systems.spider import CsvSpider


def main(event_id, overwrite=False):
    filename = 'race-%d.csv' % event_id

    if not os.path.exists(filename) or overwrite:
        with open(filename, 'w', newline='') as out:
            spider = CsvSpider(event_id=event_id, out=out)
            spider.go()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage:\n\tpython go.py <EVENT_ID> --overwrite\n')
        sys.exit(1)

    event_id = int(sys.argv[1])
    overwrite = sys.argv[-1] == '--overwrite'
    main(event_id, overwrite)
