import logging

from splint import SplintResult, attributes


@attributes(tag='tag1', ruid="1_1", level=1, phase="prototype")
def check_result_1_1():
    """Check result 1.1 docstring"""
    logging.info("check_result_1_1")
    yield SplintResult(status=True, msg="Result 1.1")


@attributes(tag='tag1', ruid="1_2", level=2, phase="prototype")
def check_result_1_2():
    """Check result 1.2 docstring"""
    logging.info("check_result_1_2")
    yield SplintResult(status=True, msg="Result 1.2")
