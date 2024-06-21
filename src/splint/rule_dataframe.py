"""
Useful rules for checking data frames.
"""
from typing import Generator

import numpy as np
import pandas as pd

from .splint_exception import SplintException
from .splint_result import SR


def rule_validate_df_schema(df: pd.DataFrame,
                            columns: list[str] | None = None,
                            no_null_columns: list[str] | None = None,
                            int_columns: list[str] | None = None,
                            float_columns: list[str] | None = None,
                            str_columns: list[str] | None = None,
                            row_min_max: tuple[int, int] | None = None,
                            allowed_values: list | None = None,
                            empty_ok: bool = False) -> Generator[SR, None, None]:
    """
        Validate a DataFrame schema based on given conditions.

        Parameters:
        df (pd.DataFrame): DataFrame to be validated.
        columns (list[str], optional): Columns to validate. Defaults to None.
        no_null_columns (list[str], optional): Columns without null values. Defaults to None.
        int_columns (list[str], optional): Integer type columns. Defaults to None.
        float_columns (list[str], optional): Float type columns. Defaults to None.
        str_columns (list[str], optional): String type columns. Defaults to None.
        row_min_max (tuple[int,int], optional): Min/max row numbers in DataFrame. Defaults None.
        empty_ok (bool, optional): When True, empty DataFrame is valid. Defaults to False.

        Raises:
        SplintException: If df is None, min_rows/max_rows are negative, or min_rows > max_rows.

        Yields:
        SR: Object with validation status (True if condition met, False otherwise)
        and a description of the result.
        """

    def check_dtype(col_, dtype, dtype_name):
        if df[col_].dtype in dtype:
            yield SR(status=True, msg=f"Column {col_} is of type {dtype_name}.")
        else:
            yield SR(status=False, msg=f"Column {col_} is not of type {dtype_name}.")

    def check_null(col_):
        null_count = df[col_].isnull().sum()
        if null_count == 0:
            yield SR(status=True, msg=f"Column {col_} has no null values.")
        else:
            yield SR(status=False, msg=f"Column {col_} has {null_count} null values.")

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
    else:
        pass

    if no_null_columns:
        for column in no_null_columns:
            yield from check_null(column)

    if int_columns:
        for column in int_columns:
            yield from check_dtype(column, ['int64', 'int32'], 'int')

    if float_columns:
        for column in float_columns:
            yield from check_dtype(column, ['float64', 'float32'], 'float')

    if str_columns:
        for col in str_columns:
            yield from check_dtype(col, ['object'], 'object')

    if allowed_values and columns:
        for column in columns:
            if df[column].isin(allowed_values).all():
                yield SR(status=True, msg=f"All values in column {column} are in {allowed_values}.")
            else:
                yield SR(status=False,
                         msg=f"Some values in column {column} are not in {allowed_values}.")

    if row_min_max:
        min_rows, max_rows = row_min_max
        if min_rows < 0 or max_rows < 0:
            raise SplintException("min_rows and max_rows must be non-negative integers.")
        if min_rows > max_rows:
            raise SplintException("min_rows must be less than or equal to max_rows.")

        if min_rows <= len(df) <= max_rows:
            yield SR(status=True,
                     msg=f"Data frame has {len(df)} rows. Range = {min_rows} - {max_rows} rows.")
        else:
            yield SR(status=False,
                     msg=f"Data frame has {len(df)} rows. Range = {min_rows} - {max_rows} rows.")

    if not any([columns, no_null_columns, int_columns,
                float_columns, str_columns, row_min_max, allowed_values]):
        yield SR(status=False,
                 msg="There are no columns to check.")


def rule_validate_df_values_by_col(df: pd.DataFrame,
                                   positive: list[str] | str | None = None,
                                   non_negative: list[str] | str | None = None,
                                   percent: list[str] | str | None = None,
                                   min_: tuple[float, list[str]] | None = None,
                                   max_: tuple[float, list[str]] | None = None,
                                   negative: list[str] | str | None = None,
                                   non_positive: list[str] | str | None = None,
                                   correlation: list[str] | str | None = None,
                                   probability: list[str] | str | None = None):
    """
        Validate DataFrame schema based on given conditions. Parameters are as follows:

        Parameters:
        - df (pd.DataFrame): DataFrame to validate.
        - columns (list[str], optional): Col names to validate. Defaults to None.
        - no_null_columns (list[str], optional): Cols shouldn't have null values. Defaults to None.
        - int_columns (list[str], optional): Columns of integer type. Defaults to None.
        - float_columns (list[str], optional): Columns of float type. Defaults to None.
        - str_columns (list[str], optional): Columns of string type. Defaults to None.
        - row_min_max (Tuple[int,int], optional): Min/max # of rows in DataFrame. Defaults to None.
        - allowed_values (list, optional): Allowed values in columns. Defaults to None.
        - empty_ok (bool, optional): If True, empty DataFrame is valid. Defaults to False.

        Raises:
        - SplintException: If df is None, min_rows/max_rows aren't positive integers, or
                           min_rows is > max_rows.

        Yields:
        - SR: An obj with the status of the validation (True if condition is met, False otherwise)
              and a message describing the result.
    """

    if df is None or df.empty:
        raise SplintException("Dataframe is empty or None")

    # Let lazy people specify a columns by string
    positive = positive.split(',') if isinstance(positive, str) else positive
    non_negative = non_negative.split(',') if isinstance(non_negative, str) else non_negative
    percent = percent.split(',') if isinstance(percent, str) else percent
    negative = negative.split(',') if isinstance(negative, str) else negative
    non_positive = non_positive.split(',') if isinstance(non_positive, str) else non_positive
    correlation = correlation.split(',') if isinstance(correlation, str) else correlation
    probability = probability.split(',') if isinstance(probability, str) else probability

    # min_/max_ are (float,str) or (float,list),
    if min_:
        min_ = (min_[0], min_[1].split(',')) if isinstance(min_[1], str) else min_
    if max_:
        max_ = (max_[0], max_[1].split(',')) if isinstance(max_[1], str) else max_

    conditions = [positive, non_negative, negative, non_positive,
                  percent, min_, max_, probability, correlation]

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
                yield SR(status=False, msg=f"Not all values in {col} are non-positive.")
