
from src import splint



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
