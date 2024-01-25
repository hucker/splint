import src.splint as splint
import pytest
import time


def test_function_attributes():
    """ Test arbutrary attributes """
    @splint.attributes(tag="tag", phase="phase", level=1, weight=100, skip=False)
    def func():
        pass

    assert func.tag == "tag"
    assert func.phase == "phase"
    assert func.level == 1
    assert func.weight == 100
    assert func.skip is False

def test_def_function_attributes():
    """ Check default tags """
    @splint.attributes(tag="")
    def func():
        pass

    assert func.tag == ""
    assert func.phase == ""
    assert func.level == 1
    assert func.weight == 100
    assert func.skip is False



def test_basic_func_call():
    @splint.attributes(tag="Test")
    def func():
        """Test Function"""
        yield splint.SR(status=True, msg="It works")
    sfunc = splint.SplintFunction(None, func)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It works"
        assert result.doc == "Test Function"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.info_msg == ""
        assert result.tag == "Test"

def test_basic_func_call_timing():
    @splint.attributes(tag="Timing")
    def func():
        """Test Timing Function"""
        time.sleep(1.1)
        yield splint.SR(status=True, msg="Timing works")
    sfunc = splint.SplintFunction(None, func)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "Timing works"
        assert result.doc == "Test Timing Function"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == ""
        assert result.info_msg == ""
        assert result.tag == "Timing"
        assert result.runtime_sec > 1.0

def test_info_warning_func_call():
    @splint.attributes(tag="InfoWarning")
    def func():
        """Test Complex Function"""
        yield splint.SR(status=True, msg="It still works",warn_msg="Warning",info_msg="Info")
    sfunc = splint.SplintFunction(None, func)

    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True
        assert result.msg == "It still works"
        assert result.doc == "Test Complex Function"
        assert result.skipped is False
        assert result.except_ is None
        assert result.warn_msg == "Warning"
        assert result.info_msg == "Info"
        assert result.tag == "InfoWarning"
