import responses
from sport_systems.spider import SportSystemResultsSpider


@responses.activate
def test_total(response_1):
    responses.add(
        responses.GET,
        'http://www.sportsystems.co.uk/ss/results/data/1740/?link=N&posStart=0&count=1',  # NOQA
        body=response_1,
        match_querystring=True
    )

    def callback(res):
        pass

    spider = SportSystemResultsSpider(event_id=1740, callback=callback)
    assert spider.total_count == 3857
