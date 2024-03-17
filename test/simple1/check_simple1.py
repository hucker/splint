"""DocString for check_simple1"""
from src import splint


def check_hello():
    """DocString for check_hello"""
    yield splint.SplintResult(status=True, msg="Result check_hello")
