import responses
from sport_systems.spider import Spider


@responses.activate
def test_total(response_1):
    responses.add(
        responses.GET,
        'http://www.sportsystems.co.uk/ss/results/data/1740/?posStart=0&count=20',  # NOQA
        body=response_1,
        match_querystring=True
    )
    spider = Spider(event_id=1740)
    assert spider.total_count == 3857
