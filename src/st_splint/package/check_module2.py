import src.splint as splint
from splint import SR


@splint.attributes(tag="tag1",ruid="m2_f1")
def check_module2_func1():
    yield SR(status=True, msg="Always passes")


@splint.attributes(tag="tag2",ruid='m2_f2')
def check_module2_func2():
    yield SR(status=False, msg="Always fails")
