import pytest
from src.splint.splint_result import SplintResult
from src.splint.splint_result import group_by
SR = SplintResult

@pytest.fixture
def results():
    return [SR(status=True, msg="msg1", tag="tag1", level=1),
            SR(status=True, msg="msg1", tag="tag2", level=1),
            SR(status=True, msg="msg1", tag="tag1", level=1),
            SR(status=True, msg="msg2", tag="tag2", level=1),
            SR(status=True, msg="msg2", tag="tag1", level=1),
            SR(status=True, msg="msg2", tag="tag2", level=1),
            SR(status=True, msg="msg3", tag="tag1", level=1),
            SR(status=True, msg="msg3", tag="tag2", level=1),
            SR(status=True, msg="msg3", tag="tag1",level=2),
            SR(status=True, msg="msg4", tag="tag2",level=2),
            SR(status=True, msg="msg4", tag="tag1",level=2),
            SR(status=True, msg="msg4", tag="tag2",level=2),
            SR(status=True, msg="msg5", tag="tag1",level=2),
            SR(status=True, msg="msg5", tag="tag2",level=2),
            SR(status=True, msg="msg5", tag="tag1",level=2),
            SR(status=True, msg="msg6", tag="tag2",level=2),
            ]

def test_group_by_empty():
    results = []
    g1 = group_by(results, ["tag"])
    assert len(g1) == 0

    g2 = group_by(results, ["msg"])
    assert len(g2) == 0

    g3 = group_by(results, ["level"])
    assert len(g3) == 0


def test_group_by_1(results):
    g1 = group_by(results, ["tag"])
    assert len(g1) == 2

    g2 = group_by(results, ["msg"])
    assert len(g2) == 6

    g3 = group_by(results, ["level"])
    assert len(g3) == 2

def test_null_groupby(results):
    g1 = group_by(results, [])
    assert len(g1) == 16


def test_group_by_2(results):

    g1 = group_by(results, ["msg", "level"])
    assert len(g1["msg1"][1]) == 3
    assert len(g1["msg2"][1]) == 3
    assert len(g1["msg3"][1]) == 2
    assert len(g1["msg3"][2]) == 1
    assert g1["msg6"][2][0].msg == "msg6"
    assert g1["msg6"][2][0].tag == "tag2"
    assert g1["msg6"][2][0].level == 2
