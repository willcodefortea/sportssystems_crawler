from sportsystems_crawler import parser


def test_parsing(response_1):
    results = parser.parse(response_1)
    assert len(list(results)) == 20


def test_total_count(response_1):
    total = parser.extract_total(response_1)
    assert total == 3857
