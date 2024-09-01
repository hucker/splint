
"""
Set of baseline rules that uses the pyfilesystem module to OS-agnostic checks on things
about the file system, file existing, age etc.
"""

from typing import Generator

from sqlalchemy import MetaData,Table,Engine
from splint import SR


def rule_sql_table_schema(engine: Engine,
                          table: str,
                          expected_columns: list[str],
                          extra_columns_ok:bool=True) -> Generator[SR, None, None]:
    """
    Take a connection, a table, and column names and verify that the table has those columns
    Args:
        conn: SQLAlchemy engine object
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
    metadata.bind = engine
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
