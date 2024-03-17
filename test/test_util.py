import pytest

import splint
from splint import splint_result
from splint import splint_exception
from splint import str_to_bool

@pytest.mark.parametrize("input_val",
                         ['true', 't', 'yes', 'y', '1', 'on'])
def test_def_str_to_bool_true(input_val):
    assert str_to_bool(input_val) == True


# Test when str_to_bool return False
@pytest.mark.parametrize("input_val",
                         ['false', 'f', 'no', 'n', '0', 'off'])
def test_def_str_to_bool_false(input_val):
    assert str_to_bool(input_val) == False

import pytest


@pytest.mark.parametrize("input_val", ['x', 'foo', 'whatever','',' '])
def test_except(input_val):
    with pytest.raises(ValueError):
        _ = str_to_bool(input_val)

@pytest.mark.parametrize("input_val, default_val",
                         [('x', True),
                          ('x', False),
                          ('foo', True),
                          ('foo', False),
                          ('fum', True),
                          ('fum', False),
                          ('whatever', True),
                          ('whatever', False)])
def test_def_str_to_bool(input_val, default_val):
    if default_val is True:
        assert str_to_bool(input_val, default_val) == True
    else:
        assert str_to_bool(input_val, default_val) == False

@pytest.mark.parametrize("input_val, default_val, expected_output",
                         [('f', True, False),
                          ('f', False, False),
                          ('t', True, True),
                          ('t', False, True)])
def test_def_str_no_override(input_val, default_val, expected_output):
    assert str_to_bool(input_val, default_val) == expected_output