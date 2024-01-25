from collections import namedtuple
import src.splint as splint
import pytest


@pytest.fixture
def simple1_pkg():
    return splint.SplintPackage(folder="./test/simple1",name="Simple1")


@pytest.fixture
def decorator1_pkg():
    return splint.SplintPackage(folder="./test/decorator1",name="Decorator1")


@pytest.fixture
def decorator2_pkg():
    return splint.SplintPackage(folder="./test/decorator2",name="Decorator2")

@pytest.fixture
def skip_pkg():
    return splint.SplintPackage(folder="./test/skip",name="Skip")

def test_sugar():
    r1 = splint.SplintResult(status=True, msg="msg")
    r2 = splint.SR(status=True, msg="msg")
    assert r1 == r2

def test_load_1_package_load(simple1_pkg):
    assert len(simple1_pkg.modules) == 1
    assert "check_simple1" in (m.module_name for m in simple1_pkg.modules)
    m = simple1_pkg.get("check_simple1")
    assert m
    assert m.module_name == "check_simple1"
    assert m.doc == "DocString for check_simple1"


def test_run_simple(simple1_pkg):
    results = simple1_pkg.run_all()
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "Result check_hello"
    assert results[0].doc == "DocString for check_hello"
    assert results[0].function_name == "check_hello"
    assert results[0].skipped is False
    assert results[0].except_ is None
    assert results[0].warn_msg == ""
    assert results[0].info_msg == ""
    assert results[0].tag == ""


def test_dec1(decorator1_pkg):
    assert len(decorator1_pkg.modules) == 1
    assert "check_dec" in (m.module_name for m in decorator1_pkg.modules)
    m = decorator1_pkg.get("check_dec")
    assert m
    assert m.module_name == "check_dec"
    assert m.doc == "DocString for check_dec"


def test_run_dec1(decorator1_pkg):
    results = decorator1_pkg.run_all()
    assert len(decorator1_pkg.modules) == 1
    assert "check_dec" in (m.module_name for m in decorator1_pkg.modules)
    assert len(results) == 1
    assert results[0].status is True
    assert results[0].msg == "Result check_dec"
    assert results[0].doc == "DocString for check_dec"
    assert results[0].function_name == "check_dec"
    assert results[0].skipped is False
    assert results[0].except_ is None
    assert results[0].warn_msg == ""
    assert results[0].info_msg == ""
    assert results[0].tag == "tag1"
    assert results[0].level == 1


def test_run_lambda(decorator1_pkg):
    results = decorator1_pkg.run_all(filter_func=lambda x: x.tag == "tag1")
    assert len(decorator1_pkg.modules) == 1
    assert "check_dec" in (m.module_name for m in decorator1_pkg.modules)
    assert len(results) == 1

    func = splint.keep_tag("tag1")

    results = decorator1_pkg.run_all(filter_func=func)
    assert len(results) == 1

    func = splint.keep_level(1)

    results = decorator1_pkg.run_all(filter_func=func)
    assert len(results) == 1


def test_run_lambda2(decorator1_pkg):
    results = decorator1_pkg.run_all(filter_func=lambda x: x.tag == "tag2")
    assert len(results) == 0


def test_decorator2(decorator2_pkg):
    """Run all the package should have 6 pass results."""
    results = decorator2_pkg.run_all()
    assert len(decorator2_pkg.modules) == 1
    assert len(results) == 6
    assert sum(r.status for r in results) == 6


def test_decorator2_tag_keep(decorator2_pkg):
    """For each tag there should only be 1 result."""
    for i in range(1, 7):
        tag = f"tag{i}"
        results = decorator2_pkg.run_all(filter_func=splint.keep_tag(tag))
        assert len(decorator2_pkg.modules) == 1
        assert len(results) == 1
        assert results[0].tag == tag
        assert sum(r.status for r in results) == 1

def test_decorator2_tag_filter(decorator2_pkg):
    """For each tag there should only be 1 result."""
    for i in range(1, 7):
        tag = f"tag{i}"
        results = decorator2_pkg.run_all(filter_func=splint.filter_tag(tag))
        assert len(decorator2_pkg.modules) == 1
        assert len(results) == 5
        assert sum(r.status for r in results) == 5

def test_decorator2_tag_filter_multi(decorator2_pkg):
    """For each tag there should only be 1 result."""
    tags = ["tag1", "tag2"]
    results = decorator2_pkg.run_all(filter_func=splint.filter_tag(*tags))
    assert len(decorator2_pkg.modules) == 1
    assert len(results) == 4
    assert sum(r.status for r in results) == 4

def test_decorator2_tag_keep_multi(decorator2_pkg):
    """For each tag there should only be 1 result."""
    tags = ["tag1", "tag2"]
    results = decorator2_pkg.run_all(filter_func=splint.keep_tag(*tags))
    assert len(decorator2_pkg.modules) == 1
    assert len(results) == 2
    assert sum(r.status for r in results) == 2

def test_decorator2_level_keep(decorator2_pkg):
    """For each level there should be the same number of tests as the level."""
    for level in range(1, 4):
        results = decorator2_pkg.run_all(filter_func=splint.keep_level(level))
        assert len(decorator2_pkg.modules) == 1
        assert len(results) == level
        assert sum(r.status for r in results) == level


# Define a namedtuple type for your tests
Test = namedtuple('Test', ['func', 'counts'])

def test_decorator2_level_keep3(decorator2_pkg):
    """For each level there should be the same number of tests as the level.
    and they should all pass"""

    # This is level and count pairs
    d_ge = Test(splint.keep_level_gte, {1: 6, 2: 5, 3: 3})
    d_g = Test(splint.keep_level_gt, {1: 5, 2: 3, 3: 0})
    d_le = Test(splint.keep_level_lte, {1: 1, 2: 3, 3: 6})
    d_l = Test(splint.keep_level_lt, {1: 0, 2: 1, 3: 3})

    tests = [d_ge, d_g, d_le, d_l]
    for test in tests:
        for level, count in test.counts.items():
            print(f"func={test.func} level={level} count={count}")
            results = decorator2_pkg.run_all(filter_func=test.func(level))
            assert len(decorator2_pkg.modules) == 1
            assert len(results) == count
            assert sum(r.status for r in results) == count


def test_decorator2_level_filter(decorator2_pkg):
    """For each level there should be the same number of tests as the level.
    and they should all pass"""

    # This is level and count pairs
    d_ge = Test(splint.filter_level_lt, {1: 6, 2: 5, 3: 3})
    d_g = Test(splint.filter_level_lte, {1: 5, 2: 3, 3: 0})
    d_le = Test(splint.filter_level_gt, {1: 1, 2: 3, 3: 6})
    d_l = Test(splint.filter_level_gte, {1: 0, 2: 1, 3: 3})

    tests = [d_ge, d_g, d_le, d_l]
    for test in tests:
        for level, count in test.counts.items():
            print(f"func={test.func} level={level} count={count}")
            results = decorator2_pkg.run_all(filter_func=test.func(level))
            assert len(decorator2_pkg.modules) == 1
            assert len(results) == count
            assert sum(r.status for r in results) == count


def test_skip_pkg(skip_pkg):
    """Verify skip behavior, this module has two functions and one is skipped."""
    results = skip_pkg.run_all()
    assert len(skip_pkg.modules) == 1
    assert len(results) == 1
    assert sum(r.status for r in results) == 1
    assert results[0].skipped is False
    assert results[0].function_name == "check_no_skip"

def test_pkg_name(skip_pkg,decorator1_pkg,decorator2_pkg,simple1_pkg):
    assert skip_pkg.name == "Skip"
    assert decorator1_pkg.name == "Decorator1"
    assert decorator2_pkg.name == "Decorator2"
    assert simple1_pkg.name == "Simple1"