"""
This module provides functions for conducting PDF file checks and handling their responses.

The main feature is to extract tables with the following headings.

RuleId  Description Status


"""


from typing import Generator, List, Tuple

import numpy as np
import pandas as pd
import camelot
from .splint_result import SR
from .splint_exception import SplintException

def extract_tables_from_pdf(file_path: str,
                            required_columns: List[str] = ["RuleId", "Note", "Status"],
                            pages: str = 'all') -> List[pd.DataFrame]:
    """
    Extracts tables from a PDF file that include specified columns, and returns them in a list.

    Args:
        file_path: The path to the PDF file.
        required_columns: The list of columns that must be present in the table.
            Defaults to ["RuleId", "Description", "Status"].
        pages: The pages of the PDF to process. It could be 'all', a range like '1-7', or
            specific pages like '1,3,5'. Defaults to 'all'.

    Returns:
        A list of pandas DataFrames representing the tables extracted from the PDF file.
    """
    filtered_tables = []
    try:
        tables = camelot.read_pdf(file_path, flavor='stream', pages=pages)
        for table in tables:
            # Take the table and make the first row the column headers
            df = table.df
            df.columns = df.iloc[0]
            df = df.drop(df.index[0])
            if set(required_columns).issubset(df.columns):
                filtered_tables.append(df)
    except Exception as e:
        raise Exception(f"Error extracting tables from PDF: {str(e)}")

    return filtered_tables

def rule_pdf_rule_id(file_path: str,rule_id: str) -> str:
    tables = extract_tables_from_pdf(file_path)
    for table in tables:
        if "RuleId" in table.columns:
            df = table[table["RuleId"] == rule_id]
            if not df.empty and len(df)==1:
                rule_data = df.iloc[0]
                status =rule_data["Status"] in ('1','Pass','Yes')
                yield SR(status=status,msg = rule_data['Note'])
