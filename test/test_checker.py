from typing import List

import pytest

import src.splint as splint


@pytest.fixture
def func1():
    @splint.attributes(tag="t1", level=1, ruid="suid_1")
    def func1():
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(None, func1)


@pytest.fixture
def func2():
    @splint.attributes(tag="t2", level=2, ruid="suid_2")
    def func2():
        yield splint.SplintResult(status=True, msg="It works2")

    return splint.SplintFunction(None, func2)


def test_function_list(func1, func2):
    """Test that run_all returns results"""

    funcs = [func1, func2]

    ch = splint.SplintChecker(functions=funcs)
    ch.pre_collect()
    ch.prepare()
    results = ch.run_all()

    assert len(results) == 2
    assert results[0].status is True
    assert results[1].status is True


def test_filtered_function_list(func1, func2):
    """Test building a custom filter function"""

    ch = splint.SplintChecker(functions=[func1, func2])

    def filter1(f: splint.SplintFunction):
        return f.ruid == "suid_1"

    def filter2(f: splint.SplintFunction):
        return f.ruid == "suid_2"

    ch.pre_collect()
    ch.prepare(filter_functions=[filter1])

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works1"
    assert results[0].ruid == "suid_1"

    # Rerun with second filter
    ch.prepare(filter_functions=[filter2])

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works2"
    assert results[0].ruid == "suid_2"



def test_built_exclude_ruids(func1, func2):
    """Test exclude_ruids"""
    funcs = [func1, func2]

    filters = [splint.exclude_ruids(["suid_1"])]

    ch = splint.SplintChecker(functions=funcs)
    ch.pre_collect()
    ch.prepare(filter_functions=filters)

    results = ch.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "It works2"
    assert results[0].ruid == "suid_2"


def test_filter_all(func1, func2):
    """Test filtering everything"""

    filters = [splint.exclude_ruids(["suid_1", "suid_2"])]

    ch = splint.SplintChecker(functions=[func1, func2])
    ch.pre_collect()
    ch.prepare(filter_functions=filters)

    results = ch.run_all()
    assert len(results) == 0


def test_built_exclude_tags(func1, func2):
    """Test exclude_tags"""

    filters = [splint.exclude_tags(["t2"])]

    ch = splint.SplintChecker(functions=[func1, func2])
    ch.pre_collect()
    ch.prepare(filter_functions=filters)

    results: List[splint.SplintResult] = ch.run_all()
    assert len(results) == 1
    assert results[0].tag == "t1"
    assert results[0].msg == "It works1"

    filters = [splint.exclude_tags(["t1"])]

    ch = splint.SplintChecker(functions=[func1, func2])
    ch.pre_collect()
    ch.prepare(filter_functions=filters)

    results: List[splint.SplintResult] = ch.run_all()
    assert len(results) == 1
    assert results[0].tag == "t2"
    assert results[0].msg == "It works2"


def test_as_dict(func1,func2):
    ch = splint.SplintChecker(functions=[func1, func2])
    ch.pre_collect()
    ch.prepare()
    results = ch.run_all()
    d = ch.as_dict()
    assert isinstance(d, dict)

    assert d["functions"] == ['func1', 'func2']
    assert d["modules"] == []
    assert d["package_count"] == 0
    assert d["module_count"] == 0
    assert d["function_count"] == 2
    assert d["passed_count"] == 2
    assert d["failed_count"] == 0
    assert d["total_count"] == 2

def test_progress(capsys, func1, func2):
    funcs = [func1, func2]
    ch = splint.SplintChecker(functions=funcs, progress_callback=splint.debug_progress)
    ch.pre_collect()
    ch.prepare()
    _ = ch.run_all()
    captured = capsys.readouterr()
    assert captured[0] == 'Start Rule Check\nFunc Start func1\n+Func done.\nFunc Start func2\n+Func done.\nRule Check Complete.\n'

