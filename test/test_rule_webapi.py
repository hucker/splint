
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


def test_bad_web_api():
    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_web_api(url='https://swapi.dev/api/mylittepony',
                                       json_d={'name': 'Luke Skywalker'})

    # This will fail because the API request will fail
    for result in check_rule1():
        assert not result.status

    # This runs the same test but tells that it expects a 404.  More exhaustive testing
    # could be performed here, but  we aren't testing requests.  This shows that we can
    # detect status from
    @splint.attributes(tag="tag")
    def check_rule2():
        yield from splint.rule_web_api(url='https://swapi.dev/api/mylittepony',
                                       json_d={'name': 'Luke Skywalker'},
                                       expected_response=404)

    for result in check_rule2():
        assert result.status


def test_web_api():
    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_web_api(url='https://swapi.dev/api/people/1',
                                       json_d={'name': 'Luke Skywalker', 'height': '172', 'mass': '77'})

    @splint.attributes(tag="tag")
    def check_rule_bad_mass():
        yield from splint.rule_web_api(url='https://swapi.dev/api/people/1',
                                       json_d={'name': 'Luke Skywalker', 'height': '172', 'mass': '78'})

    for result in check_rule1():
        assert result.status

    for result in check_rule_bad_mass():
        assert not result.status




def convert_integers_to_strings(d):
    """This takes my integer test dictionaries and turns them into strings for test purposees"""
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
        ({},{},None,'Null Test'),
        ({'a':1},{'a':1},None,'Simple pass'),
        ({'a':1},{'a':2},{'a':1},'Simple fail'),
        ({'a':1},{'A':1},{'a':1},'Simple fail'),
        ({'a':1},{'b':1},{'a':1},'Simple no key'),
        ({'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}},{'a': 1, 'b': 2, 'c': {'d': 3, 'e': 5}},  {'c': {'e': 4}},"Nest diff"),
        ({'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}}, {'a': 1, 'b': 2, 'c': {'d': 3, 'e': 4}, 'f': 6},None,'Nested diff'),
    ]

    for sub_set,main_set,expected_result,msg in tests:
        result = is_mismatch(sub_set, main_set)
        assert result == expected_result

    # now convert to string values
    for sub_set,main_set,expected_result,msg in tests:
        sub_set = convert_integers_to_strings(sub_set)
        main_set = convert_integers_to_strings(main_set)
        expected_result = convert_integers_to_strings(expected_result)
        result = is_mismatch(sub_set, main_set)
        assert result == expected_result
