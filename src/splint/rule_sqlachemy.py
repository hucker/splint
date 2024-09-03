"""
Set of baseline rules that uses the pyfilesystem module to OS-agnostic checks on things
about the file system, file existing, age etc.
"""

from typing import Generator

from sqlalchemy import Engine, MetaData, Table
from sqlalchemy.sql.type_api import TypeEngine

from .splint_result import SR


def rule_sql_table_col_name_schema(engine: Engine,
                                   table: str,
                                   expected_columns: list[str],
                                   extra_columns_ok: bool = True) -> Generator[SR, None, None]:
    """
    Take a connection, a table, and column names and verify that the table has those columns.
    Note that this does NOT verify the data types of the columns.
    Args:
        engine: SQLAlchemy engine object
        table: Name of the table
        columns: List of expected column names

    Returns:
        A generator yielding assertion results for each column
    """

    if not table:
        yield SR(status=False, msg="Table name cannot be blank.")
        return

    if not expected_columns:
        yield SR(status=False, msg="Column list cannot be empty.")
        return

    count = 0

    for expected_column in expected_columns:
        if not expected_column.strip():
            yield SR(status=False, msg="Column names cannot be empty.")
            count += 1

    if count:
        return

    # Get the table's metadata
    metadata = MetaData()
    table_obj = Table(table, metadata, autoload_with=engine)
    actual_columns = set(table_obj.columns.keys())

    # Verify expected columns exist
    for column in expected_columns:
        if column in actual_columns:
            yield SR(status=True, msg=f"Column '{column}' is correctly present in table {table}")
        else:
            yield SR(status=False, msg=f"Missing column in table {table}: {column}")

    # If extra columns existing in the database is OK then don't check
    if not extra_columns_ok:
        extra_columns = actual_columns - set(expected_columns)

        # This is very subtle.  We want the ordering of actual columns here  rather than iterating
        # over the set (that varies with python version).   For small sets this isnt to terrible
        for column in actual_columns:
            if column in extra_columns:
                yield SR(status=False, msg=f"Unexpected column in table {table}: {column}")


def rule_sql_table_schema(engine: Engine,
                          table: str,
                          expected_columns: list[tuple[str, TypeEngine]],
                          extra_columns_ok: bool = True) -> Generator[SR, None, None]:
    """
    Take a connection, a table, and column names and verify that the table has those columns
    AND the correct types.
    Args:
        engine: SQLAlchemy engine object
        table: Name of the table
        expected_columns: List of expected column name,type pairs
        extra_columns_ok: (default=True) Ignore additional columns in the table.

    Returns:
        A generator yielding assertion results for each column
    """
    if not table:
        yield SR(status=False, msg="Table name cannot be blank.")
        return

    if not expected_columns:
        yield SR(status=False, msg="Column list cannot be empty.")
        return

    # Get the table's metadata
    metadata = MetaData()
    table_obj = Table(table, metadata, autoload_with=engine)
    actual_columns = {column.name: column.type for column in table_obj.columns}

    # Verify expected columns exist and have correct types
    for expected_column, expected_type in expected_columns:
        actual_type = actual_columns.get(expected_column)

        # Check if column exists
        if actual_type:
            # Remove any qualifiers from the SQLAlchemy type to get base type
            unqualified_actual_type = actual_type.__class__.__name__
            unqualified_expected_type = expected_type.__class__.__name__

            # Check if types match
            if unqualified_actual_type == unqualified_expected_type:
                # pylint: disable=line-too-long
                yield SR(status=True,
                         msg=f"Column '{expected_column}' of type '{expected_type}' is correctly present in table {table}")
            else:
                # pylint: disable=line-too-long
                yield SR(status=False,
                         msg=f"Column '{expected_column}' has incorrect type. Expected: '{unqualified_expected_type}', got: '{unqualified_actual_type}'")
        else:
            yield SR(status=False, msg=f"Missing column in table {table}: {expected_column}")

    # If extra columns existing in the database is OK then don't check
    if not extra_columns_ok:
        extra_columns = set(actual_columns.keys()) - set(column for column, _ in expected_columns)
        for column in extra_columns:
            yield SR(status=False, msg=f"Unexpected column in table {table}: {column}")
