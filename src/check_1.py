from  splint import SplintPackage, SplintResult, SplintException
import logging

def check_result_1_1():
    logging.info("check_result_1_1")
    yield SplintResult(status=True,msg="Result 1.1")


def check_result_1_2():
    logging.info("check_result_1_2")
    yield SplintResult(status=True,msg="Result 1.2")