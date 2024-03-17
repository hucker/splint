"""DocString for check_dec"""
from src import splint


@splint.attributes(tag='tag1', level=1)
def check_dec():
    """DocString for check_dec"""
    yield splint.SplintResult(status=True, msg="Result check_dec")
