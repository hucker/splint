import pathlib
import requests
import time
from src import splint


def test_rule_file_exist():
    """Verify that we can use the rule_path_exists rule in a function that we build."""
    @splint.attributes(tag="tag")
    def check_rule1():
        for result in splint.rule_path_exists(path_="./test/rule_files_/my_file.txt"):
            yield result

    @splint.attributes(tag="tag")
    def check_rule2():
        yield from splint.rule_path_exists(path_="./test/rule_files_/my_file.dummy")

    s_func1 = splint.SplintFunction('', check_rule1)
    s_func2 = splint.SplintFunction('', check_rule2)
    for result in s_func1():
        assert result.status

    for result in s_func2():
        assert result.status is False




def test_rule_large_files():
    """Verify that we can use the rule_path_exists rule in a function that we build."""
    @splint.attributes(tag="tag")
    def check_rule1():
        for result in splint.rule_large_files(folder="./test/rule_files_",pattern="*.txt", max_size=10000):
            yield result


    @splint.attributes(tag="tag")
    def check_rule2():
        for result in splint.rule_large_files(folder="./test/rule_files_",pattern="*.txt", max_size=50):
            yield result


    s_func1 = splint.SplintFunction('', check_rule1)
    for result in s_func1():
        assert result.status

    s_func2 = splint.SplintFunction('', check_rule2)

    for result in s_func2():
        assert result.status is False




def test_stale_file():
    """Verify that we can use the rule_stale_files rule in a function that we build."""
    file_path = pathlib.Path("./test/rule_files_")

    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_stale_files(folder=file_path, pattern="my_file*.txt", days=0, hours=0, minutes=0, seconds=1)


    # Touch the file
    pathlib.Path("./test/rule_files_/my_file.txt").touch()

    s_func1 = splint.SplintFunction('', check_rule1)
    for result in s_func1():
        assert result.status

    # Wait for a second
    time.sleep(2)

    for result in s_func1():
        assert not result.status


def test_urls():
    urls = [ "https://www.google.com", "https://www.yahoo.com", "https://www.bing.com"]
    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_url_200(urls=urls)

    for result in check_rule1():
        assert result.status

def test_max_files():
    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_max_files(folders=["./test/rule_files_"], max_files=10)

    for result in check_rule1():
        assert result.status

    @splint.attributes(tag="tag")
    def check_rule2():
        yield from splint.rule_max_files(folders=["./test/rule_files_"], max_files=1)

    for result in check_rule2():
        assert result.status is False

def test_web_api():
    @splint.attributes(tag="tag")
    def check_rule1():
        yield from splint.rule_web_api(url='https://swapi.dev/api/people/1',
                                       json_d={'name':'Luke Skywalker','height':'172','mass':'77'})

    @splint.attributes(tag="tag")
    def check_rule_badmass():
        yield from splint.rule_web_api(url='https://swapi.dev/api/people/1',
                                       json_d={'name':'Luke Skywalker','height':'172','mass':'78'})
    for result in check_rule1():
        assert result.status

    for result in check_rule_badmass():
        assert not result.status
