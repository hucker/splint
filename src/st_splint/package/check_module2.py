import src.splint as splint
from splint import SR
import time


@splint.attributes(tag="tag1",ruid="m2_f1",level=1)
def check_module2_func1():
    "Another always passing function"
    time.sleep(.5)
    yield SR(status=True, msg="Always passes")


@splint.attributes(tag="tag2",ruid='m2_f2',level=2)
def check_module2_func2():
    "THis thing always fails"
    time.sleep(.5)
    yield SR(status=False, msg="Always fails")
