import src.splint as splint
from splint import SR
import time

@splint.attributes(tag="tag1",ruid="m1_f1",level=1)
def check_module1_func1():
    """ Simple always passing function"""
    time.sleep(.5)
    yield SR(status=True,msg="Always passes")

@splint.attributes(tag="tag2",ruid="m1_f2",level=2)
def check_module1_func2():
    """ Simple always Failing Function"""
    time.sleep(.5)
    yield SR(status=True,msg="Always passes")

@splint.attributes(tag="tag3",ruid="m1_f3",level=3)
def check_module1_func3():
    """ Skips because flag set"""
    time.sleep(.5)
    yield SR(status=False,msg="Always passes",skipped=True)