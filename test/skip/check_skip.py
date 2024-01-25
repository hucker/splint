"""DocString for check_dec"""
import src.splint as splint


"""
Test that functions are skipped with the skip flag.
"""

@splint.attributes(skip=True)
def check_skip():
    """DocString for skip"""
    yield splint.SplintResult(status=True,msg="Result check_dec1")

@splint.attributes(skip=False)
def check_no_skip():
    """DocString for skip"""
    yield splint.SplintResult(status=True,msg="Result check_dec2")

