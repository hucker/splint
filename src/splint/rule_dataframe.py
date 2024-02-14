
from typing import List, Generator, Tuple
import pandas as pd
import numpy as np
from .splint_result import SplintResult as SR
from .splint_exception import SplintException



def rule_validate_df_schema(df: pd.DataFrame,
                   columns:List[str]=None,
                   no_null_columns:List[str]=None,
                   int_columns:List[str]=None,
                   float_columns:List[str]=None,
                   str_columns:List[str]= None,
                   row_min_max:Tuple[int,int]=None,
                   allowed_values:List=None,
                   empty_ok:bool=False) -> Generator[SR,None,None]:
    """
    Validate the schema of a DataFrame based on given conditions.

    Parameters:
    df (pd.DataFrame): The DataFrame to validate.
    columns (List[str], optional): The list of column names to validate. Defaults to None.
    no_null_columns (List[str], optional): List of columns that should not contain null values. Defaults to None.
    int_columns (List[str], optional): List of columns that should be of integer type. Defaults to None.
    float_columns (List[str], optional): List of columns that should be of float type. Defaults to None.
    str_columns (List[str], optional): List of columns that should be of string type. Defaults to None.
    row_min_max (Tuple[int,int], optional): Tuple specifying the minimum and maximum number of rows in the DataFrame. Defaults to None.
    empty_ok (bool, optional): If True, an empty DataFrame is considered valid. Defaults to False.

    Raises:
    SplintException: If df is None, min_rows and max_rows are not non-negative integers, or min_rows is greater than max_rows.

    Yields:
    SR: A status report object containing the status of the validation (True if the condition is met, False otherwise)
        and a message describing the result.
    """
    def check_dtype(column, dtype, dtype_name):
        if df[column].dtype in dtype:
            yield SR(status=True, msg=f"Column {column} is of type {dtype_name}.")
        else:
            yield SR(status=False, msg=f"Column {column} is not of type {dtype_name}.")

    def check_null(column):
        null_count = df[column].isnull().sum()
        if null_count == 0:
            yield SR(status=True, msg=f"Column {column} has no null values.")
        else:
            yield SR(status=False, msg=f"Column {column} has {null_count} null values.")

    if df is None:
        raise SplintException("Data frame is None.")

    if df.empty:
        yield SR(status=empty_ok, msg="Data frame is empty.")
        return

    if columns:
        if set(columns).issubset(df.columns):
            yield SR(status=True, msg=f"All columns {columns} are in data frame.")
        else:
            yield SR(status=False, msg=f"Columns {set(columns)-set(df.columns)} are not in data frame.")

    if no_null_columns:
        for column in no_null_columns:
            yield from check_null(column)

    if int_columns:
        for column in int_columns:
            yield from check_dtype(column, ['int64','int32'], 'int')

    if float_columns:
        for column in float_columns:
            yield from check_dtype(column, ['float64','float32'], 'float')

    if str_columns:
        for column in str_columns:
            yield from check_dtype(column, ['object'], 'object')

    if allowed_values:
        for column in columns:
            if df[column].isin(allowed_values).all():
                yield SR(status=True, msg=f"All values in column {column} are in {allowed_values}.")
            else:
                yield SR(status=False, msg=f"Some values in column {column} are not in {allowed_values}.")


    if row_min_max:
        min_rows, max_rows = row_min_max
        if min_rows < 0 or max_rows < 0:
            raise SplintException("min_rows and max_rows must be non-negative integers.")
        if min_rows > max_rows:
            raise SplintException("min_rows must be less than or equal to max_rows.")

        if len(df) >= min_rows and len(df) <= max_rows:
            yield SR(status=True, msg=f"Data frame has between {min_rows} and {max_rows} rows.")
        else:
            yield SR(status=False, msg=f"Data frame has {len(df)} rows, which is not between {min_rows} and {max_rows}.")

    if not columns and not no_null_columns and not int_columns and not float_columns and not str_columns and not row_min_max and not allowed_values:
        yield SR(status=False, msg="There are no columns to check")

def rule_validate_df_column(df: pd.DataFrame,
                         columns:List[str]=None,
                         positive:bool=None,
                         non_negative:bool=None,
                         percent:float=None,
                         rng:Tuple[float,float]=None,
                         negative:bool=None,
                         non_positive:bool=None):
    """
    Validate specified columns in a DataFrame based on given conditions.

    Parameters:
    df (pd.DataFrame): The DataFrame to validate.
    columns (List[str], optional): The list of column names to validate. Defaults to None.
    positive (bool, optional): If True, checks if all values in the columns are positive. Defaults to None.
    non_negative (bool, optional): If True, checks if all values in the columns are non-negative. Defaults to None.
    percent (float, optional): If True, checks if all values in the columns are between 0 and 100. Defaults to None.
    rng (Tuple[float,float], optional): If specified, checks if all values in the columns are within this range. Defaults to None.
    negative (bool, optional): If True, checks if all values in the columns are negative. Defaults to None.
    non_positive (bool, optional): If True, checks if all values in the columns are non-positive. Defaults to None.

    Raises:
    SplintException: If df is None, no columns are specified, more than one condition is specified,
                     specified columns are not in the DataFrame, no conditions are specified, or
                     the range is not a tuple or list of two numbers with the first less than the second.

    Yields:
    SR: A status report object containing the status of the validation (True if the condition is met, False otherwise)
        and a message describing the result.
    """
    if df is None:
        raise SplintException("Data frame is None.")

    if not columns:
        raise SplintException("No columns specified.")

    conditions = [positive, non_negative, negative, non_positive, percent, bool(rng)]
    if conditions.count(True) > 1:
        raise SplintException("Only one condition should be specified.")

    if not set(columns).issubset(df.columns):
        raise SplintException(f"Columns {set(columns)-set(df.columns)} are not in data frame.")

    if not any([positive, non_negative, percent, rng, negative, non_positive]):
        raise SplintException("No conditions specified.")

    if rng and (not isinstance(rng,(tuple,list)) or len(rng) != 2  or rng[0]>rng[1]):
        raise SplintException("Range must be a tuple or list of the form (low, high)")

    if positive:
        if np.all(df[columns] > 0):
            yield SR(status=True, msg="All specified columns are positive.")
        else:
            yield SR(status=False, msg="Not all specified columns are positive.")

    if non_negative:
        if np.all(df[columns] >= 0):
            yield SR(status=True, msg="All specified columns are non-negative.")
        else:
            yield SR(status=False, msg="Not all specified columns are non-negative.")

    if percent:
        if np.all((df[columns] >= 0) & (df[columns] <= 100)):
            yield SR(status=True, msg="All specified columns are a percent.")
        else:
            yield SR(status=False, msg="Not all specified columns are a percent.")

    if rng:
        low, high = rng
        if np.all((df[columns] >= low) & (df[columns] <= high)):
            yield SR(status=True, msg=f"All specified columns are in range [{low},{high}].")
        else:
            yield SR(status=False, msg=f"Not all specified columns are in range [{low},{high}].")

    if negative:
        if np.all(df[columns] < 0):
            yield SR(status=True, msg="All specified columns are negative.")
        else:
            yield SR(status=False, msg="Not all specified columns are negative.")

    if non_positive:
        if np.all(df[columns] <= 0):
            yield SR(status=True, msg="All specified columns are non-positive.")
        else:
            yield SR(status=False, msg="Not all specified columns are non-positive.")
