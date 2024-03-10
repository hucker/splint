import itertools

import pandas as pd
import pytest

import src.splint as splint


@pytest.fixture(scope="module")
def good_abc_df():
    return pd.DataFrame({'a': [1, 2, 3], 'b': [1, 2, 3], 'c': [1, 2, 3], 'd': [1, 2, 3]})


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


def test_min_max():
    df = pd.DataFrame({'a': [1, 2, 3, 4, 5, 6, 7, 8, 9]})
    result1 = list(splint.rule_validate_df_schema(df, row_min_max=(1, 10)))
    result2 = list(splint.rule_validate_df_schema(df, row_min_max=(1, 5)))
    result3 = list(splint.rule_validate_df_schema(df, row_min_max=(100, 200)))

    assert all([r.status for r in result1])
    assert all([not r.status for r in result2])
    assert all([not r.status for r in result3])


def test_bad_min_max():
    df = pd.DataFrame({'a': [1, 2, 3, 4, 5, 6, 7, 8, 9]})

    def check_bad_min_max():
        yield from splint.rule_validate_df_schema(df, row_min_max=(10, 0))

    sfunc = splint.SplintFunction(check_bad_min_max)
    results = list(sfunc())
    assert len(results) == 1
    assert results[0].except_


def test_allowed_values():
    df = pd.DataFrame({'a': [1, 1, 1, 3, 3, 3, 5, 5, 5]})
    result1 = list(splint.rule_validate_df_schema(df, columns=['a'], allowed_values=(1, 3, 5)))
    result2 = list(splint.rule_validate_df_schema(df, columns=['a'], allowed_values=(1, 3, 5, 7)))
    result3 = list(splint.rule_validate_df_schema(df, columns=['a'], allowed_values=(0, 1)))

    assert all([r.status for r in result1])
    assert all([r.status for r in result2])
    assert any([not r.status for r in result3])


def test_str_columns():
    df = pd.DataFrame({'a': ["a", "b", "c"], 'b': ["d", "e", "f"], 'c': [1, 2, 3]})
    result = list(splint.rule_validate_df_schema(df, str_columns=['a', 'b']))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, str_columns=['a']))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, str_columns=['b']))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, str_columns=['c']))
    assert not all([r.status for r in result])


def test_schema_empty():
    df = pd.DataFrame()
    result = list(splint.rule_validate_df_schema(df, empty_ok=True))
    assert all([r.status for r in result])

    result = list(splint.rule_validate_df_schema(df, empty_ok=False))
    assert not all([r.status for r in result])


def test_schema_nothing(df_val):
    def check_nothing_schema():
        yield from splint.rule_validate_df_schema(df_val
                                                  )

    sfunc = splint.SplintFunction(check_nothing_schema)
    results = list(sfunc())
    assert len(results) == 1
    assert results[0].status is False
    assert results[0].msg == "There are no columns to check."


def test_exceptions():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_schema(df, row_min_max=(-1, 10)))

    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_schema(df, row_min_max=(1, -10)))

    with pytest.raises(splint.SplintException):
        list(splint.rule_validate_df_schema(None))


def generate_all_permutations(elements):
    """
    Permutations of all lengths

    Args:
        elements (list): The list of elements to generate permutations from.

    Yields:
        tuple: Yields permutations as tuples.
    """
    for r in range(1, len(elements) + 1):
        for perm in itertools.permutations(elements, r):
            yield perm


def test_all_column_checks(good_abc_df):
    """ Make sure that ANY way to specifiy the columns works"""
    df = good_abc_df

    # Every one of these should pass
    for cols in generate_all_permutations(['a', 'b', 'c', 'd']):
        for type_ in [list, tuple]:
            tcols = type_(cols)
            results = list(splint.rule_validate_df_schema(df, columns=tcols))
            for result in results:
                assert result.status


def test_bad_column_checks(good_abc_df):
    """ We know this dataframe has abcd columns, lets try every way to make abce and make sure they all fail"""
    df = good_abc_df.copy()
    for cols in itertools.permutations(['a', 'b', 'c', 'e']):
        results = list(splint.rule_validate_df_schema(df, columns=cols))
        # In all cases there should be one fail and 3 pass
        assert len(results) == 1
        assert results[0].status is False


def test_all_columns():
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4.4, 5.5, 6.6], 'c': [7, None, 9], 'd': [10.1, None, 12.2]})
    result = list(
        splint.rule_validate_df_schema(df, columns=['a', 'b', 'c', 'd'], no_null_columns=['a', 'b'], int_columns=['a'],
                                       float_columns=['b']))
    assert all([r.status for r in result])


@pytest.fixture(scope="module")
def df_val():
    return pd.DataFrame({'A': [-1.0, 0, 1.0],
                         'B': [-0.5, 0, .5],
                         'C': [-2, -10, -50],
                         'D': [0, 0, 2],
                         'E': [0, 10, 100],
                         'F': [1, 10, 100],
                         'G': [0, .4, 1.0],
                         },
                        )


def test_df_null_df():
    """ Should generate an error when a null data frame is passed in """
    df = pd.DataFrame()

    def check_df():
        yield from splint.rule_validate_df_values_by_col(df=df, non_negative=['E', 'F'])

    s_func = splint.SplintFunction(check_df)

    results = list(s_func())
    assert len(results) == 1
    assert results[0].except_
    assert results[0].status is False


def test_no_conditions(df_val):
    """ Should generate exception result when no checks are requested"""

    def check_df():
        yield from splint.rule_validate_df_values_by_col(df=df_val)

    s_func = splint.SplintFunction(check_df)
    results = list(s_func())
    assert len(results) == 1
    assert not results[0].status
    assert results[0].except_


def test_df_column_values_pass(df_val):
    df = df_val
    results = list(splint.rule_validate_df_values_by_col(df=df, non_negative=['E', 'F']))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, correlation=['A']))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, percent=['E']))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, positive=['F']))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, negative=['C']))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, probability=['G']))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, min_=(0, ['G']), max_=(1, ['G'])))
    for result in results:
        assert result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, non_positive=['C']))
    for result in results:
        assert result.status


def test_rule_no_column_check(df_val):
    df = df_val

    def check_rules():
        yield from splint.rule_validate_df_values_by_col(df=df)

    sfunc = splint.SplintFunction(check_rules)
    results = list(sfunc())
    assert len(results) == 1
    assert results[0].status is False
    assert results[0].except_


def test_df_column_values_fail(df_val):
    df = df_val

    results = list(splint.rule_validate_df_values_by_col(df=df, non_negative='A'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, non_positive='F'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, correlation='E,F,C'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, percent='A,B,C'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, positive='A,B,C,D,E,G'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, negative='D,E,F,G'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, probability='A,B,C,D,E,F'))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, max_=(-1, 'A,B,D,E,G')))
    for result in results:
        assert not result.status

    results = list(splint.rule_validate_df_values_by_col(df=df, min_=(2, 'A,B,D,E,G')))
    for result in results:
        assert not result.status
