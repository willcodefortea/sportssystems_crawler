"""Statistics module."""

from collections import namedtuple, defaultdict

Result = namedtuple('Result', ['time', 'name'])
DEFAULT_PERCENTILES = (50, 66, 75, 80, 90, 95, 98, 99, 100)


def create_buckets(results):
    """Group a sorted result set into buckets."""
    buckets = defaultdict(lambda: [])

    for result in results:
        key = result.time.strftime('%H-%M')
        buckets[key].append(result)

    return buckets


def generate_percentiles(results, percentiles=DEFAULT_PERCENTILES):
    """Percentage distribution of the results.

    I.e. At what point had 50%, 75% and 90% of results completed?
    """
    data = []
    total = len(results)
    cur_index = 0

    if not results:
        return data

    for percentile in percentiles:
        for index, result in enumerate(results[cur_index:], start=cur_index):
            if (index / total) * 100 > percentile:
                data.append((percentile, result.time))
                cur_index = index
                break

    if percentiles[-1] == 100:
        # Special case for the final result
        data.append((100, results[-1].time))

    return data
