import pytest

import src.splint as splint


@pytest.fixture
def simple1():
    @splint.attributes(tag="t1", level=1, ruid="suid_1")
    def func1():
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(None, func1)


def test_json(simple1):
    ch = splint.SplintChecker(functions=[simple1])
    ch.pre_collect()
    ch.prepare()
    results = ch.run_all()
    d = ch.as_dict()
