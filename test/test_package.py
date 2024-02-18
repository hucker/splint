import pytest

from src import splint


@pytest.fixture
def simple1_pkg():
    return splint.SplintPackage(folder="./simple1", name="Simple1")


@pytest.fixture
def decorator1_pkg():
    return splint.SplintPackage(folder="./decorator1", name="Decorator1")


@pytest.fixture
def decorator2_pkg():
    return splint.SplintPackage(folder="./decorator2", name="Decorator2")


@pytest.fixture
def skip_pkg():
    return splint.SplintPackage(folder="./skip", name="Skip")


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


def test_load_2_packages_load(decorator1_pkg, decorator2_pkg):
    assert len(decorator1_pkg.modules) == 1
    assert "check_dec" in (m.module_name for m in decorator1_pkg.modules)
    m = decorator1_pkg.get("check_dec")
    assert m
    assert m.module_name == "check_dec"
    assert m.doc == "DocString for check_dec"

    assert len(decorator2_pkg.modules) == 1
    assert "check_dec_complex" in (m.module_name for m in decorator2_pkg.modules)
    m = decorator2_pkg.get("check_dec_complex")
    assert m
    assert m.module_name == "check_dec_complex"
    assert m.doc == "DocString for check_dec_complex"
