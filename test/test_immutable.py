"""
test_immutable.py

This module contains tests for verifying the immutability of three data structures: ImmutableList,
ImmutableDict, and ImmutableDataFrame. These classes are designed to prevent modifications of list,
dictionary, and DataFrame instances respectively to ensure data integrity.

The module is using pytest and its fixtures feature for setting up initial objects. The main strategy
of this module is trying to invoke all writable/mutating methods provided by Python for lists, dictionaries,
and pandas DataFrames on instances of ImmutableList, ImmutableDict, and ImmutableDataFrame.
The expected outcome of these operations is the raise of SplintException, indicating successful prevention of
mutation in these collections.

Tests for ImmutableList cover methods:
 - __setitem__
 - __delitem__
 - append
 - extend
 - insert
 - remove
 - pop
 - clear
 - sort
 - reverse

Tests for ImmutableDict cover methods:
 - __setitem__
 - __delitem__
 - pop
 - popitem
 - clear
 - update
 - setdefault

Tests for ImmutableDataFrame cover methods:
 - __setitem__
 - __delitem__
 - append
 - pop
 - drop
 - insert

These tests are designed to make sure that any attempts to modify instances of these classes would be blocked
and raise the appropriate exception, consistent with the intention of preserving immutability.
"""

import pandas as pd
import pytest

from src import splint
from src.splint import SplintException


@pytest.fixture
def env_df():
    return splint.SplintEnvDataFrame(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))


@pytest.fixture(scope="module")
def env_list():
    return splint.SplintEnvList([1, 2, 3, 4, 5])


def test_list_setitem(env_list):
    with pytest.raises(SplintException):
        env_list[0] = 100


def test_list_delitem(env_list):
    with pytest.raises(SplintException):
        del env_list[0]


def test_list_append(env_list):
    with pytest.raises(SplintException):
        env_list.append(6)


def test_list_extend(env_list):
    with pytest.raises(SplintException):
        env_list.extend([7, 8, 9])


def test_list_insert(env_list):
    with pytest.raises(SplintException):
        env_list.insert(0, 10)


def test_list_remove(env_list):
    with pytest.raises(SplintException):
        env_list.remove(1)


def test_list_pop(env_list):
    with pytest.raises(SplintException):
        env_list.pop(0)


def test_list_clear(env_list):
    with pytest.raises(SplintException):
        env_list.clear()


def test_list_sort(env_list):
    with pytest.raises(SplintException):
        env_list.sort()


def test_list_reverse(env_list):
    with pytest.raises(SplintException):
        env_list.reverse()


# Define a fixture to provide the test target
@pytest.fixture
def env_dict():
    return splint.SplintEnvDict({"a": 1, "b": 2, "c": 3})


def test_dict_setitem(env_dict):
    with pytest.raises(SplintException):
        env_dict["a"] = 100


def test_dict_delitem(env_dict):
    with pytest.raises(SplintException):
        del env_dict["a"]


def test_dict_pop(env_dict):
    with pytest.raises(SplintException):
        env_dict.pop("a")


def test_dict_popitem(env_dict):
    with pytest.raises(SplintException):
        env_dict.popitem()


def test_clear(env_dict):
    with pytest.raises(SplintException):
        env_dict.clear()


def test_dict_update(env_dict):
    with pytest.raises(SplintException):
        env_dict.update({"a": 0, "d": 4})


def test_dict_setdefault(env_dict):
    with pytest.raises(SplintException):
        env_dict.setdefault("d", 4)


def test_df_setitem(env_df):
    with pytest.raises(SplintException):
        env_df["a"] = [7, 8, 9]


def test_df_delitem(env_df):
    with pytest.raises(SplintException):
        del env_df["a"]


def test_df_append(env_df):
    with pytest.raises(SplintException):
        env_df.append({"a": 10, "b": 11}, ignore_index=True)


def test_df_pop(env_df):
    with pytest.raises(SplintException):
        env_df.pop("a")


def test_drop(env_df):
    with pytest.raises(SplintException):
        env_df.drop("a", axis=1)


def test_df_insert(env_df):
    with pytest.raises(SplintException):
        env_df.insert(1, "c", [7, 8, 9])


@pytest.fixture
def func_list():
    @splint.attributes(tag="t1")
    def func_list(env_list):
        env_list[0] = 'a'
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(func_list)


@pytest.fixture
def func_dict():
    @splint.attributes(tag="t1")
    def func_dict(env_dict):
        env_dict['a'] = 100
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(func_dict)


@pytest.fixture
def func_set():
    @splint.attributes(tag="env_set")
    def func_list(env_set):
        env_set.clear()
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(func_list)


def test_splint_function_writing_to_env(func_list, func_dict, func_set):
    env = {'env_list': [1, 2, 3], 'env_dict': {'a': 10, 'b': 11}, 'env_set': set((1, 2, 3))}

    ch = splint.SplintChecker(check_functions=[func_dict], env=env, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_

    ch = splint.SplintChecker(check_functions=[func_list], env=env, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_

    ch = splint.SplintChecker(check_functions=[func_set], env=env, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 1
    assert results[0].except_
