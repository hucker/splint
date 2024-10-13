
from src import splint
from src.splint.rule_webapi import is_mismatch


def test_urls():
    urls = ["https://www.google.com", "https://www.yahoo.com", "https://www.bing.com"]

    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_url_200(urls=urls)

    for result in check_rule1():
        assert result.status


def test_bad_urls():
    urls = ["https://www.google.com/doesnotexist", "https://www.yahooXXXXXX"]

    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_url_200(urls=urls)

    for result in check_rule1():
        assert not result.status



def test_missing_web_api():

    # Try to get a non existent webapi end point
    @splint.attributes(tag="tag")
    def check_rule2():
        yield from splint.rule_web_api(url='https://httpbin.org/json1',
                                       json_d={'name': 'Luke Skywalker'},
                                       expected_response=404,
                                       timeout_sec=3)

    for result in check_rule2():
        assert result.status



def test_web_api():
    expected_json = {
        "slideshow": {
            "author": "Yours Truly",
            "date": "date of publication",
            "slides": [
                {
                    "title": "Wake up to WonderWidgets!",
                    "type": "all"
                },
                {
                    "items": [
                        "Why <em>WonderWidgets</em> are great",
                        "Who <em>buys</em> WonderWidgets"
                    ],
                    "title": "Overview",
                    "type": "all"
                }
            ],
            "title": "Sample Slide Show"
        }
    }
    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_web_api(url='https://httpbin.org/json',
                                       json_d=expected_json,
                                       timeout_sec=10)
    

    for result in check_rule1():
        assert result.status
    
    # Now make it fail
    expected_json["slideshow"]["author"] = "Chuck"
    for result in check_rule1():
        assert not result.status
        
def convert_integers_to_strings(d):
    """This takes my integer test dictionaries and turns them into strings for test purposes"""
    if not d:
        return d
    for key, value in d.items():
        if isinstance(value, int):
            d[key] = str(value)
        elif isinstance(value, dict):
            convert_integers_to_strings(value)
    return d


def test_get_difference():
    tests = [
        ({}, {}, None, 'Null Test'),
        ({'a': 1}, {'a': 1}, None, 'Simple pass'),
        ({'a': 1}, {'a': 2}, {'a': 1}, 'Simple fail'),
        ({'a': 1}, {'A': 1}, {'a': 1}, 'Simple fail'),
        ({'a': 1}, {'b': 1}, {'a': 1}, 'Simple no key'),
        (
            {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}, {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 5}}, {'c': {'e': 4}},
            "Nest diff"),
        ({'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}, {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}, 'f': 6}, None, 'Nested diff'),
    ]

    for sub_set, main_set, expected_result, msg in tests:
        result = is_mismatch(sub_set, main_set)
        assert result == expected_result

    # now convert to string values
    for sub_set, main_set, expected_result, msg in tests:
        sub_set = convert_integers_to_strings(sub_set)
        main_set = convert_integers_to_strings(main_set)
        expected_result = convert_integers_to_strings(expected_result)
        result = is_mismatch(sub_set, main_set)
        assert result == expected_result
