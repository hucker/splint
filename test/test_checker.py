import pytest

import src.splint as splint


@pytest.fixture
def func1():
    @splint.attributes(tag="t1", level=1, phase='p1', ruid="suid_1")
    def func1():
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(func1)


@pytest.fixture
def func2():
    @splint.attributes(tag="t2", level=2, phase='p2', ruid="suid_2")
    def func2():
        yield splint.SplintResult(status=True, msg="It works2")

    return splint.SplintFunction(func2)


@pytest.fixture
def func3():
    @splint.attributes(tag="t3", level=3, phase='p3', ruid="suid_3")

    def func3():
        yield splint.SplintResult(status=True, msg="It works3")

    return splint.SplintFunction(func3)


@pytest.fixture
def func4():
    @splint.attributes(finish_on_fail=True)
    def func():
        """ Because finish on fail is set, this function will only yield 3 results."""
        yield splint.SplintResult(status=True, msg="It works1")
        yield splint.SplintResult(status=True, msg="It works2")
        yield splint.SplintResult(status=False, msg="It works3")
        yield splint.SplintResult(status=True, msg="It works4")

    return splint.SplintFunction(func)

def test_finish_on_fail(func4):
    """ Because func4 has finish_on_fail is set, this function will only yield 3 results rather then 4"""
    ch =  splint.SplintChecker(check_functions=[func4], auto_setup=True)
    results = ch.run_all()
    assert len(results) == 3
    assert results[0].status is True
    assert results[1].status is True
    assert results[2].status is False


def test_abort_on_fail(func4):
    """
    Abort on fail exits the whole rule checking engine.

    """

    # When we run the first case where the same function with finish on fail is called
    # twice, this should return 3 results for each run, since the func is configured to
    # return after the first false.  6 total results.
    ch =  splint.SplintChecker(check_functions=[func4, func4], auto_setup=True)
    results = ch.run_all()
    assert len(results) == 3+3

    # Now we'll set it up again with the abort on fail set to true.  This will fail out
    # immediately on the whole test when the first fail occurs.
    ch =  splint.SplintChecker(check_functions=[func4, func4], auto_setup=True, abort_on_fail=True)
    results = ch.run_all()
    assert len(results) == 3



def test_function_list(func1, func2):
    """Test that run_all returns results"""

    funcs = [func1, func2]

    ch = splint.SplintChecker(check_functions=funcs, auto_setup=True)
    results = ch.run_all()

    assert len(results) == 2
    assert results[0].status is True
    assert results[1].status is True
    assert ch.score == 100.0


def test_checker_tag_ordering(func1, func2, func3):
    """Verify we can order tests by lambda over tags"""

    # should end up func1,func2,func3
    funcs = [func3, func1, func2]
    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    run_list = ch.prepare(order_function=splint.splint_checker.orderby_tag())
    assert run_list == [func1, func2, func3]


def test_checker_ruid_ordering(func1, func2, func3):
    """Verify we can order tests by lambda over ruids"""

    funcs = [func3, func1, func2]
    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    run_list = ch.prepare(order_function=splint.splint_checker.orderby_ruid())
    assert run_list == [func1, func2, func3]


def test_filtered_function_list(func1, func2):
    """Test building a custom filter function"""

    ch = splint.SplintChecker(check_functions=[func1, func2])

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


def test_builtin_filter_ruids(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.exclude_ruids(["suid_1"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[splint.exclude_ruids(["suid_1", "suid_2"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.keep_ruids(["suid_3"])])


    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[splint.keep_ruids(["suid_1", "suid_2"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}



def test_builtin_filter_phase(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.exclude_phases(["p1"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[splint.exclude_phases(["p1", "p2"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}


    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.keep_phases(["p3"])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[splint.keep_phases(["p1", "p2"])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_level(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.exclude_levels([1])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[splint.exclude_levels([1, 2])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.keep_levels([3])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[splint.keep_levels([1, 2])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}


def test_builtin_filter_tags(func1, func2, func3):
    """Test exclude_ruids"""

    # Functions in random order
    funcs = [func3, func1, func2]

    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.exclude_tags(['t1'])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func2, func3}

    s_funcs = ch.prepare(filter_functions=[splint.exclude_tags(['t1', 't2'])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}


    ch = splint.SplintChecker(check_functions=funcs)
    ch.pre_collect()
    s_funcs = ch.prepare(filter_functions=[splint.keep_tags(['t3'])])

    assert len(s_funcs) == 1
    assert set(s_funcs) == {func3}

    s_funcs = ch.prepare(filter_functions=[splint.keep_tags(['t1', 't2'])])

    assert len(s_funcs) == 2
    assert set(s_funcs) == {func1, func2}



def test_null_check():
    """Test exclude_ruids"""
    with pytest.raises(splint.SplintException):
        funcs = []

        ch = splint.SplintChecker(check_functions=funcs, auto_setup=True)

        _ = ch.run_all()


def test_null_checker_types():
    bad_list_type = [1]
    bad_value_type = 1
    with pytest.raises(splint.SplintException):
        _ = splint.SplintChecker(check_functions=bad_list_type)
    with pytest.raises(splint.SplintException):
        _ = splint.SplintChecker(modules=bad_list_type)
    with pytest.raises(splint.SplintException):
        _ = splint.SplintChecker(packages=bad_list_type)

    with pytest.raises(splint.SplintException):
        _ = splint.SplintChecker(check_functions=bad_value_type)
    with pytest.raises(splint.SplintException):
        _ = splint.SplintChecker(modules=bad_value_type)
    with pytest.raises(splint.SplintException):
        _ = splint.SplintChecker(packages=bad_value_type)


def test_filter_all(func1, func2):
    """Test filtering everything"""

    filters = [splint.exclude_ruids(["suid_1", "suid_2"])]

    ch = splint.SplintChecker(check_functions=[func1, func2])
    ch.pre_collect()
    ch.prepare(filter_functions=filters)

    results = ch.run_all()
    assert len(results) == 0


def test_as_dict(func1, func2):
    ch = splint.SplintChecker(check_functions=[func1, func2], auto_setup=True)
    _ = ch.run_all()
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
    ch = splint.SplintChecker(check_functions=funcs, progress_callback=splint.debug_progress, auto_setup=True)
    _ = ch.run_all()
    captured = capsys.readouterr()
    assert captured[0] == 'Start Rule Check\nFunc Start func1\n+Func done.\nFunc Start func2\n+Func done.\nRule Check Complete.\nScore = 100.0\n'
