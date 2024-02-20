import logging

from splint import SplintResult, attributes


@attributes(tag='tag2', ruid="2_1", level=3, phase="release")
def check_result_2_1():
    """Check result 2.1 docstring"""
    logging.info("check_result_2_1")
    yield SplintResult(status=True, msg="Result 2.1")


@attributes(tag='tag2', ruid="2_2", level=4, phase="release")
def check_result_2_2():
    """Check result 2.2 docstring"""
    logging.info("check_result_2_2")
    yield SplintResult(status=True, msg="Result 2.2")


@attributes(tag='tag1', ruid="2_3", level=5, phase="release")
def check_exception_2_3():
    """Check result 2.3 docstring"""
    logging.info("check_exception_2_3")
    raise 1 / 0
