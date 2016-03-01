
import os
import sys
from sport_systems import csv_handler, stats


def main(event_id, overwrite=False):
    filename = 'race-%d.csv' % event_id

    if not os.path.exists(filename) or overwrite:
        with open(filename, 'w', newline='') as out:
            csv_handler.build(event_id, out)

    with open(filename, 'r') as fin:
        results = csv_handler.build_results(fin)

    percentiles = stats.generate_percentiles(results)

    print ('Percentage of completing runners within a certain time')
    for percentile, time in percentiles:
        print ('\t%s%%\t%s' % (percentile, time))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Usage:\n\tpython go.py <EVENT_ID> --overwrite\n')
        sys.exit(1)

    event_id = int(sys.argv[1])
    overwrite = sys.argv[-1] == '--overwrite'
    main(event_id, overwrite)
