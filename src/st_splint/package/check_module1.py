import src.splint as splint
from splint import SR

@splint.attributes(tag="tag1",ruid="m1_f1")
def check_module1_func1():
    """ Simple always passing function"""
    yield SR(status=True,msg="Always passes")

@splint.attributes(tag="tag2",ruid="m1_f2")
def check_module1_func2():
    """ Simple always Failing Function"""
    yield SR(status=True,msg="Always passes")

@splint.attributes(tag="tag3",ruid="m1_f3")
def check_module1_func3():
    """ Skips because flag set"""
    yield SR(status=False,msg="Always passes",skipped=True)