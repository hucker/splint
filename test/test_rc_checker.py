from typing import List

import pytest

from src import splint


@pytest.fixture
def func1():
    @splint.attributes(tag="t1", level=1, phase='p1', ruid="ruid_1")
    def func1():
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(func1)


@pytest.fixture
def func2():
    @splint.attributes(tag="t2", level=2, phase='p2', ruid="ruid_2")
    def func2():
        yield splint.SplintResult(status=True, msg="It works2")

    return splint.SplintFunction(func2)


@pytest.fixture
def func3():
    @splint.attributes(tag="t3", level=3, phase='p3', ruid="ruid_3")
    def func3():
        yield splint.SplintResult(status=True, msg="It works3")

    return splint.SplintFunction(func3)


def test_nothing_rc_file(func1, func2, func3):

    rc = splint.SplintRC(display_name='rc')

    ch = splint.SplintChecker(check_functions=[func1, func2, func3], auto_setup=True)
    assert ch.phases == ['p1', 'p2', 'p3']
    assert ch.tags == ['t1', 't2', 't3']
    assert ch.ruids == ['ruid_1', 'ruid_2', 'ruid_3']
    assert ch.levels == [1, 2, 3]

    #Same assertions
    rc = splint.SplintRC(display_name='rc')
    assert ch.phases == ['p1', 'p2', 'p3']
    assert ch.tags == ['t1', 't2', 't3']
    assert ch.ruids == ['ruid_1', 'ruid_2', 'ruid_3']
    assert ch.levels == [1, 2, 3]

def test_include_tag_rc_file(func1, func2, func3):

    rc = splint.SplintRC(display_name='rc',tags=['t1'])
    ch = splint.SplintChecker(check_functions=[func1, func2, func3], auto_setup=True,rc=rc)
    assert ch.tags == ['t1']

    rc = splint.SplintRC(display_name='rc',phases=['p1'])
    ch = splint.SplintChecker(check_functions=[func1, func2, func3], auto_setup=True,rc=rc)
    assert ch.phases == ['p1']

    rc = splint.SplintRC(display_name='rc',ruids=['ruid_1'])
    ch = splint.SplintChecker(check_functions=[func1, func2, func3], auto_setup=True,rc=rc)
    assert ch.ruids == ['ruid_1']

    #TODO Fix this.  LEvels should be ints not string rep of ints.
    #rc = splint.SplintRC(display_name='rc',levels=[1])
    #ch = splint.SplintChecker(check_functions=[func1, func2, func3], auto_setup=True,rc=rc)
    #assert ch.levels == ['1']