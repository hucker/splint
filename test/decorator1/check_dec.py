"""DocString for check_dec"""
import src.splint as splint


@splint.attributes(tag='tag1',level=1)
def check_dec():
    """DocString for check_dec"""
    yield splint.SplintResult(status=True,msg="Result check_dec")