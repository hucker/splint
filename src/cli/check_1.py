from  splint import SplintPackage, SplintResult, SplintException,attributes
import logging


@attributes(ruid="1_1")
def check_result_1_1():
    """Check result 1.1 docstring"""
    logging.info("check_result_1_1")
    yield SplintResult(status=True,msg="Result 1.1")


@attributes(ruid="1_2")
def check_result_1_2():
    """Check result 1.2 docstring"""
    logging.info("check_result_1_2")
    yield SplintResult(status=True,msg="Result 1.2")