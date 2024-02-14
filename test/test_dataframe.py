

import pandas as pd
import pytest
from typing import List
import src.splint as splint


# Assuming the rule_validate_df_schema function and SR class are defined in a module named 'module'

def test_int_columns():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    result = list(splint.rule_validate_df_schema(df, int_columns=['a', 'b']))
    assert all([r.status for r in result])

def test_float_columns():
    df = pd.DataFrame({'a': [1.1, 2.2, 3.3], 'b': [4.4, 5.5, 6.6]})
    result = list(splint.rule_validate_df_schema(df, float_columns=['a', 'b']))
    assert all([r.status for r in result])

def test_no_null_columns():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, None, 6]})
    result = list(splint.rule_validate_df_schema(df, no_null_columns=['a', 'b']))
    assert not all([r.status for r in result])


def test_str_columns():
    df = pd.DataFrame({'a': ["a","b","c"], 'b': ["d","e","f"],'c': [1,2,3]})
    result = list(splint.rule_validate_df_schema(df, str_columns=['a', 'b']))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, str_columns=['a']))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, str_columns=['b']))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, str_columns=['c']))
    assert not all([r.status for r in result])


def test_empty():
    df = pd.DataFrame()
    result = list(splint.rule_validate_df_schema(df, empty_ok=True))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, empty_ok=False))
    assert not all([r.status for r in result])

def test_exceptions():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_schema(df, row_min_max=(-1, 10)))

    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_schema(df, row_min_max=(1, -10)))

    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_schema(None))

def test_all_columns():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4.4, 5.5, 6.6], 'c': [7, None, 9], 'd': [10.1, None, 12.2]})
    result = list(splint.rule_validate_df_schema(df, columns=['a', 'b', 'c', 'd'], no_null_columns=['a', 'b'], int_columns=['a'], float_columns=['b']))
    assert all([r.status for r in result])


def test_positive_check():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    result = list(splint.rule_validate_df_column(df, 'A', positive=True))
    assert len(result) == 1
    assert result[0].status == True

def test_non_negative_check():
    df = pd.DataFrame({'B': [0, 0, 0, 0, 0]})
    result = list(splint.rule_validate_df_column(df, 'B', non_negative=True))
    assert len(result) == 1
    assert result[0].status == True

def test_negative_check():
    df = pd.DataFrame({'C': [-1, -2, -3, -4, -5]})
    result = list(splint.rule_validate_df_column(df, 'C', negative=True))
    assert len(result) == 1
    assert result[0].status == True

def test_percent_check():
    df = pd.DataFrame({'D': [50, 60, 70, 80, 90]})
    result = list(splint.rule_validate_df_column(df, 'D', percent=True))
    assert len(result) == 1
    assert result[0].status == True

def test_range_check():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    result = list(splint.rule_validate_df_column(df, 'A', rng=(1, 5)))
    assert len(result) == 1
    assert result[0].status == True

def test_non_positive_check():
    df = pd.DataFrame({'C': [-1, -2, -3, -4, -5]})
    result = list(splint.rule_validate_df_column(df, 'C', non_positive=True))
    assert len(result) == 1
    assert result[0].status == True

def test_multiple_columns():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [0, 0, 0, 0, 0]})
    result = list(splint.rule_validate_df_column(df, ['A', 'B'], positive=True))
    assert len(result) == 1
    assert result[0].status == False

def test_percent_check_failure():
    df = pd.DataFrame({'E': [101, 102, 103, 104, 105]})
    result = list(splint.rule_validate_df_column(df, 'E', percent=True))
    assert len(result) == 1
    assert result[0].status == False


def test_nonexistent_column():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_column(df, ['B'], positive=True))

def test_empty_columns_list():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_column(df, [], positive=True))

def test_invalid_rng():
    df = pd.DataFrame({'A': [1, 2, 3, 4, 5]})
    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_column(df, ['A'], rng=(5, 1)))