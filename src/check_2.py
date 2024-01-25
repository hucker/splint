from  splint import SplintPackage, SplintResult, SplintException
import logging

def check_result_2_1():
    logging.info("check_result_2_1")
    yield SplintResult(status=True,msg="Result 2.1")


def check_result_2_2():
    logging.info("check_result_2_2")
    yield SplintResult(status=True,msg="Result 2.2")

def check_exception_2_3():
    logging.info("check_exception_2_3")
    raise 1 / 0