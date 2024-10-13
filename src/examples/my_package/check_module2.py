"""Sample splint module with check functions"""

import time

from src import splint
from splint import SR


@splint.attributes(tag="tag1", ruid="m2_f1", level=1, phase="proto")
def check_module2_func1():
    "Another always passing function"
    time.sleep(.5)
    yield SR(status=True, msg="Always passes")


@splint.attributes(tag="tag2", ruid='m2_f2', level=2, phase="production")
def check_module2_func2():
    "THis thing always fails"
    time.sleep(.5)
    yield SR(status=False, msg="Always fails")


@splint.attributes(tag="tag2", ruid='m2_f3', level=2, phase="production")
def check_module2_func3():
    "This thing always warns"
    time.sleep(.5)
    yield SR(status=True, warn_msg="Always warns and passes")


@splint.attributes(tag="tag2", ruid='m2_f4', level=2, phase="production")
def check_module2_func4():
    "This thing always warns"
    time.sleep(.5)
    yield SR(status=False, warn_msg="Always warns and fails")
