from  splint import SplintPackage, SplintResult, attributes
import logging

@attributes(ruid="2_1")
def check_result_2_1():
    """Check result 2.1 docstring"""
    logging.info("check_result_2_1")
    yield SplintResult(status=True,msg="Result 2.1")


@attributes(ruid="2_2")
def check_result_2_2():
    """Check result 2.2 docstring"""
    logging.info("check_result_2_2")
    yield SplintResult(status=True,msg="Result 2.2")

@attributes(ruid="2_3")
def check_exception_2_3():
    """Check result 2.3 docstring"""
    logging.info("check_exception_2_3")
    raise 1 / 0