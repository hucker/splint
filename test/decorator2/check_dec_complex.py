"""DocString for check_dec"""
import src.splint as splint


""" In this example we have a more complex decorator structure where
    we have 3 levels of decorators.  The decorators are applied to
    the functions in the following way:

    1) There is 1 tag for each function
    2) There is 1 at level 1
    3) There are 2 at level 2
    4) There are 3 at level 3

    This allows us to test the filtering by tags and levels.
"""

@splint.attributes(tag='tag1',level=1)
def check_dec11():
    """DocString for check_dec11"""
    yield splint.SplintResult(status=True,msg="Result check_dec1")

@splint.attributes(tag='tag2',level=2)
def check_dec21():
    """DocString for check_dec1"""
    yield splint.SplintResult(status=True,msg="Result check_dec2")

@splint.attributes(tag='tag3',level=2)
def check_dec22():
    """DocString for check_dec1"""
    yield splint.SplintResult(status=True,msg="Result check_dec4")

@splint.attributes(tag='tag4',level=3)
def check_dec31():
    """DocString for check_dec1"""
    yield splint.SplintResult(status=True,msg="Result check_dec31")

@splint.attributes(tag='tag5',level=3)
def check_dec32():
    """DocString for check_dec22"""
    yield splint.SplintResult(status=True,msg="Result check_dec32")

@splint.attributes(tag='tag6',level=3)
def check_dec33():
    """DocString for check_dec22"""
    yield splint.SplintResult(status=True,msg="Result check_dec33")


