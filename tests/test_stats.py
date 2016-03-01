import datetime
from sport_systems import stats


class TestBucketing(object):
    def test_bucketing(self, results_1):
        bucketed_results = stats.create_buckets(results_1)
        assert len(bucketed_results['01-10']) == 2


class TestPercentile(object):
    def test_generating(self, results_1):
        percentiles = stats.generate_percentiles(results_1)
        assert percentiles[0][1] == datetime.time(1, 30, 15)
