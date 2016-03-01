from sport_systems import csv_handler


class TestBuildResults(object):
    def test_is_sorted(self):
        with open('race-1740.csv', 'r') as csvfile:
            results = csv_handler.build_results(csvfile)

        assert results[0].name == 'Tom Jervis'
        assert results[-1].name == 'Frances Lindsay'
