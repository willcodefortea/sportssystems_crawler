
import os
import sys
from sport_systems import csv_builder


def main(event_id, overwrite=False):
    filename = 'race-%d.csv' % event_id

    if not os.path.exists(filename) or overwrite:
        with open(filename, 'w', newline='') as out:
            csv_builder.build(event_id, out)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage:\n\tpython go.py <EVENT_ID> --overwrite\n')
        sys.exit(1)

    event_id = int(sys.argv[1])
    overwrite = sys.argv[-1] == '--overwrite'
    main(event_id, overwrite)
