import pytest
import pandas as pd
import numpy as np
from  src.splint.splint_function import SplintFunction
from src.splint.rule_ndf import rule_ndf_columns_check


@pytest.fixture(scope="module")
def dataframe():
    # Make a DataFrame with 4 columns and 10 rows of random numbers
    df = pd.DataFrame(np.random.randn(10, 4), columns=list('ABCD'))
    return df


def test_rule_ndf(dataframe):
    # dataframe = 1
    def check_good_narwals_frame():
        yield from rule_ndf_columns_check(name="ABCD Dataframe",
                                          df=dataframe,
                                          expected_columns=['A', 'B', 'C', 'D'],
                                          exact=True)

    s_func1 = SplintFunction(check_good_narwals_frame)
    for result in s_func1():
        assert result.status is True

def test_rule_not_exact(dataframe):
    # dataframe = 1
    def check_good_narwals_frame():
        yield from rule_ndf_columns_check(name="ABCD Dataframe",
                                          df=dataframe,
                                          expected_columns=['A', 'B', 'C'],
                                          exact=False)

    s_func1 = SplintFunction(check_good_narwals_frame)
    for result in s_func1():
        assert result.status is True

def test_rule_ndf_missing(dataframe):
    # dataframe = 1
    def check_good_narwals_frame():
        yield from rule_ndf_columns_check(name="ABCD Dataframe",
                                          df=dataframe,
                                          expected_columns=['A', 'B', 'C','D','E'],
                                          exact=False)

    s_func1 = SplintFunction(check_good_narwals_frame)
    for result in s_func1():
        assert result.status is False
        assert "'E'" in result.msg