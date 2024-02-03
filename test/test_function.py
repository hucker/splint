import src.splint as splint
import pytest
import time


def test_func_doc_string_extract():
    @splint.attributes(tag="tag")
    def func():
        """This is a test function

        Mitigation:
        - Do something

        Owner:
        chuck@foobar.com

        Info:
        This is a
        long info string
        that needs

        help

        """
        return True
    sfunc = splint.SplintFunction(None, func)
    for result in sfunc():
        assert result.func_name == "func"
        assert result.status is True

        # NOTE: The inspect module, when used to get doc strings, will strip the leading
        #       white space from the doc string.  This is why the doc string is not
        #       indented and why you should use INSPECT.getdoc() to get the doc string.

        assert sfunc._get_section("Mitigation") == "- Do something"
        assert sfunc._get_section("Owner") == "chuck@foobar.com"
        assert sfunc._get_section("Info") == "This is a\nlong info string\nthat needs\n\nhelp"
        assert sfunc._get_section()=='This is a test function'

def test_function_attributes():
    """ Test arbitrary attributes """
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
    sfunc1 = splint.SplintFunction(None, func)

    @splint.attributes(tag="Timing")
    def fast_func():
        """Test Timing Function"""
        time.sleep(.1)
        yield splint.SR(status=True, msg="Timing works")
    sfunc2 = splint.SplintFunction(None, fast_func)

    result:splint.SplintResult = next(sfunc1())
    assert result.status is True
    assert result.skipped is False
    assert result.except_ is None
    assert result.runtime_sec > 1.0

    result:splint.SplintResult = next(sfunc2())
    assert result.status is True
    assert result.skipped is False
    assert result.except_ is None
    assert result.runtime_sec < .2

def test_info_warning_func_call():
    """ Verify that warning message gets to result"""
    @splint.attributes(tag="InfoWarning")
    def func():
        """Test Complex Function"""
        yield splint.SR(status=True, msg="It still works",warn_msg="Warning")
    sfunc = splint.SplintFunction(None, func)


    result:splint.SplintResult = next(sfunc())
    assert result.func_name == "func"
    assert result.status is True
    assert result.skipped is False
    assert result.except_ is None
    assert result.warn_msg == "Warning"

def test_divide_by_zero():
    """ Test exception handling data passes through to result """
    @splint.attributes(tag="DivideByZero")
    def func():
        """Test Exception Function"""
        return 1/0
    sfunc = splint.SplintFunction(None, func)

    result:splint.SplintResult = next(sfunc())
    assert result.status is False
    assert result.msg == "Exception 'division by zero' occurred while running func"
    assert result.doc == "Test Exception Function"
    assert result.skipped is False
    assert str(result.except_) == 'division by zero'
    assert result.tag == "DivideByZero"