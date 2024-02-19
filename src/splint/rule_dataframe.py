from typing import Generator, List, Tuple

import numpy as np
import pandas as pd

from .splint_exception import SplintException
from .splint_result import SplintResult as SR


def rule_validate_df_schema(df: pd.DataFrame,
                            columns: List[str] = None,
                            no_null_columns: List[str] = None,
                            int_columns: List[str] = None,
                            float_columns: List[str] = None,
                            str_columns: List[str] = None,
                            row_min_max: Tuple[int, int] = None,
                            allowed_values: List = None,
                            empty_ok: bool = False) -> Generator[SR, None, None]:
    """
    Validate the schema of a DataFrame based on given conditions.

    Parameters:
    df (pd.DataFrame): The DataFrame to validate.
    columns (List[str], optional): The list of column names to validate. Defaults to None.
    no_null_columns (List[str], optional): List of columns that should not contain null values. Defaults to None.
    int_columns (List[str], optional): List of columns that should be of integer type. Defaults to None.
    float_columns (List[str], optional): List of columns that should be of float type. Defaults to None.
    str_columns (List[str], optional): List of columns that should be of string type. Defaults to None.
    row_min_max (Tuple[int,int], optional): Tuple with the min/max # of rows in the DataFrame. Defaults to None.
    empty_ok (bool, optional): If True, an empty DataFrame is considered valid. Defaults to False.

    Raises:
    SplintException: If df is None, min_rows/max_rows are not non-negative integers, or min_rows is > than max_rows.

    Yields:
    SR: An object containing the status of the validation (True if the condition is met, False otherwise)
        and a message describing the result.
    """

    def check_dtype(col, dtype, dtype_name):
        if df[col].dtype in dtype:
            yield SR(status=True, msg=f"Column {col} is of type {dtype_name}.")
        else:
            yield SR(status=False, msg=f"Column {col} is not of type {dtype_name}.")

    def check_null(col):
        null_count = df[col].isnull().sum()
        if null_count == 0:
            yield SR(status=True, msg=f"Column {col} has no null values.")
        else:
            yield SR(status=False, msg=f"Column {col} has {null_count} null values.")

    if df is None:
        raise SplintException("Data frame is None.")

    if df.empty:
        yield SR(status=empty_ok, msg="Data frame is empty.")
        return

    if columns:
        if set(columns).issubset(df.columns):
            yield SR(status=True, msg=f"All columns {columns} are in data frame.")
        else:
            yield SR(status=False,
                     msg=f"Columns {set(columns) - set(df.columns)} are not in data frame.")

    if no_null_columns:
        for col in no_null_columns:
            yield from check_null(col)

    if int_columns:
        for col in int_columns:
            yield from check_dtype(col, ['int64', 'int32'], 'int')

    if float_columns:
        for col in float_columns:
            yield from check_dtype(col, ['float64', 'float32'], 'float')

    if str_columns:
        for col in str_columns:
            yield from check_dtype(col, ['object'], 'object')

    if allowed_values:
        for col in columns:
            if df[col].isin(allowed_values).all():
                yield SR(status=True, msg=f"All values in column {col} are in {allowed_values}.")
            else:
                yield SR(status=False,
                         msg=f"Some values in column {col} are not in {allowed_values}.")

    if row_min_max:
        min_rows, max_rows = row_min_max
        if min_rows < 0 or max_rows < 0:
            raise SplintException("min_rows and max_rows must be non-negative integers.")
        if min_rows > max_rows:
            raise SplintException("min_rows must be less than or equal to max_rows.")

        if len(df) >= min_rows and len(df) <= max_rows:
            yield SR(status=True,
                     msg=f"Data frame has {len(df)} rows. Range = {min_rows} - {max_rows} rows.")
        else:
            yield SR(status=False,
                     msg=f"Data frame has {len(df)} rows. Range = {min_rows} - {max_rows} rows.")

    if not any([columns, no_null_columns, int_columns, float_columns, str_columns, row_min_max, allowed_values]):
        yield SR(status=False,
                 msg="There are no columns to check")


def rule_validate_df_values_by_col(df: pd.DataFrame,
                                   positive: List[str] = None,
                                   non_negative: List[str] = None,
                                   percent: List[str] = None,
                                   min_: Tuple[float, List[str]] = None,
                                   max_: Tuple[float, List[str]] = None,
                                   negative: List[str] = None,
                                   non_positive: List[str] = None,
                                   correlation: List[str] = None,
                                   probability: List[str] = None):
    """
   Validate provided columns in a DataFrame based on different conditions such as whether
   values are positive, non-negative, in a certain percentage range, less than or
   greater than a certain minimum or maximum value, negative, non-positive or a probability.

   There is a strong argument that these should all be separate, but the case where I sure
   like typing 'a,b,c' rather than ['a','b','c'], roughly half the characters.  If your col
   names have , in them then tough luck.

   yield from rule_validate_df_values_by_column(positive='A', probability='B', negative='C')

   is hard to resist.

   Parameters:
   df (pd.DataFrame): The input DataFrame to validate.
   positive (List[str], optional): List of columns to check if all values are positive. Defaults to None.
   non_negative (List[str], optional): List of columns to check if all values are non-negative. Defaults to None.
   percent (List[str], optional): List of columns to check if all values are between 0 and 100. Defaults to None.
   min_ (Tuple[float, List[str]], optional): Tuple with minimum value and list of column names. Checks if all values
                                             in the columns are >= min value. Defaults to None.
   max_ (Tuple[float, List[str]], optional): Tuple with maximum value and list of column names. Checks if all values
                                             in the columns are <= max value. Defaults to None.
   negative (List[str], optional): List of columns to check if all values are negative. Defaults to None.
   non_positive (List[str], optional): List of columns to check if all values are non-positive. Defaults to None.
   probability (List[str], optional): List of columns to check if all values are between 0 and 1. Defaults to None.

   Raises:
   SplintException: If df is None, no cols are spec'ed or if there are incompatible values in the specified columns.

   Yields:
   SR: A status report object containing the status of the validation (True if the condition is met, False otherwise)
       and a message describing the result.
    """

    if df is None:
        raise SplintException("Data frame is None.")

    # Let lazy people specify a columns by string
    positive = positive.split(',') if isinstance(positive, str) else positive
    non_negative = non_negative.split(',') if isinstance(non_negative, str) else non_negative
    percent = percent.split(',') if isinstance(percent, str) else percent
    negative = negative.split(',') if isinstance(negative, str) else negative
    non_positive = non_positive.split(',') if isinstance(non_positive, str) else non_positive
    correlation = correlation.split(',') if isinstance(correlation, str) else correlation
    probability = probability.split(',') if isinstance(probability, str) else probability

    if min_:
        min_ = (min[0], min_[1].split(',')) if isinstance(min_[1], str) else min_
    if max_:
        max_ = (max[0], max_[1].split(',')) if isinstance(max_[1], str) else max_

    conditions = [positive, non_negative, negative, non_positive, percent, min_, max_, probability, correlation]

    if not any(conditions):
        raise SplintException("No data frame column value rules specified.")

    if positive:
        for col in positive:
            if np.all(df[col] > 0):
                yield SR(status=True, msg=f"All values in {col} are  a positive.")
            else:
                yield SR(status=False, msg=f"Not all values in {col} are  a positive.")

    if non_negative:
        for col in non_negative:
            if np.all(df[col] >= 0):
                yield SR(status=True, msg=f"All values in {col} are  a non-negative.")
            else:
                yield SR(status=False, msg=f"Not all values in {col} are  a non-negative.")

    if percent:
        # Just check 0-100
        for col in percent:
            if np.all((df[col] >= 0) & (df[col] <= 100)):
                yield SR(status=True, msg=f"All values in {col} are  a percent.")
            else:
                yield SR(status=False, msg=f"All values in {col} are a percent.")

    if probability:
        for col in probability:
            # Just check 0-100
            if np.all((df[col] >= 0.0) & (df[col] <= 1.0)):
                yield SR(status=True, msg=f"All values in {col} are probabilities.", )
            else:
                yield SR(status=False, msg=f"Not all values in {col} are probabilities.")

    if correlation:
        for col in correlation:
            # Just check 0-100
            if np.all((df[col] >= -1.0) & (df[col] <= 1.0)):
                yield SR(status=True, msg=f"All values in {col} are correlations.", )
            else:
                yield SR(status=False, msg=f"Not all values in {col} are correlations.")

    if min_:
        val, cols = min_
        for col in cols:
            if np.all((df[col] >= val)):
                yield SR(status=True, msg=f"All values in {col} are > {val}")
            else:
                yield SR(status=False, msg=f"Not all values in {col} are > {val}")
    if max_:
        val, cols = max_
        for col in cols:
            if np.all((df[col] <= val)):
                yield SR(status=True, msg=f"All values in {col} are < {val}")
            else:
                yield SR(status=False, msg=f"Not all values in {col} are < {val}")

    if negative:
        for col in negative:
            if np.all(df[col] < 0):
                yield SR(status=True, msg=f"All values in {col} are negative.")
            else:
                yield SR(status=False, msg=f"Not all values in {col} are negative.")

    if non_positive:
        for col in non_positive:
            if np.all(df[col] <= 0):
                yield SR(status=True, msg=f"All values in {col} are non-positive.")
            else:
                yield SR(status=False, msg=f"Not all valus in {col} are non-positive.")
