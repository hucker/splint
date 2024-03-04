import openpyxl

from .splint_exception import SplintException
from .splint_result import SplintResult as SR

SHEET1 = "Sheet1"
AUTO = "auto"
DESC_DEFAULT = ""
START_ROW_DEFAULT = "1"
VAL_COL_DEFAULT = "B"
DESCRIPTION_COLUMN = "A"

def _str_to_bool(s: str) -> bool:
    s = s.strip().lower()  # Remove spaces at the beginning/end and convert to lower case

    if s in ('true', 'yes', '1', 't', 'y', 'on'):
        return True
    elif s in ('false', 'no', '0', 'f', 'n', 'off',''):
        return False
    else:
        raise ValueError(f'Cannot convert {s} to a boolean')

def _column_to_number(column: str) -> int:
    number = 0
    for i, char in enumerate(reversed(column)):
        number += (ord(char.upper()) - 64) * (26 ** i)
    return number





def rule_xlsx_a1_pass_fail(wb:openpyxl.workbook, sheet=None, desc_col='A', val_col='B', row_start='1',row_end=None):
    """ This is a very blunt instrument that pulls a true/false value out of
        a specfic sheet/row/col of an Excel workbook.  It is very unforgiving
        to format changes in the work book

        Using start and end row numbers you can iterate over many items in the notebook.  If row
        end is set to 'auto' it will run until the first blank is detected in the value column.

        """
    auto = False

    if sheet is None:
        if len(wb.sheetnames) == 1:
           sheet = wb.sheetnames[0]
        else:
            if "Sheet1" in wb.sheetnames:
                sheet = "Sheet1"
            else:
                raise SplintException(f'A sheet name was not specified and Sheet1 could not be found.')
    elif sheet not in wb.sheetnames:
        raise SplintException(f'The sheet {sheet} was not found in the workbook.')

    if val_col is None:
        val_col = 'B'

    # Convert the name into a sheet
    sheet = wb[sheet]
    row_start = int(row_start)

    if row_end is None:
        row_end = row_start
    elif isinstance(row_end, str) and row_end.isdigit():
        row_end = int(row_end)
        if row_end < row_start:
            raise SplintException(f'The value for the end row must be larger than the start row {row_start=} {row_end=}.')
    elif isinstance(row_end,str) and row_end.lower() == 'auto':
        auto = True
        row_end = 1000

    val_col = _column_to_number(val_col)

    if desc_col is not None:
        desc_col = _column_to_number(desc_col)

    for row in range(row_start, row_end+1):

        value = sheet.cell(row=row, column=val_col).value
        if value is None and auto:
            break
        elif value is None:
            raise SplintException(f'Expected boolean value in row {row}')

        if desc_col is not None:
            desc = sheet.cell(row=row, column=desc_col).value
        else:
            # It is possible not to have a description column
            desc = ""

        if _str_to_bool(value):
            yield SR(status=True,msg=f"{desc}-Passed")
        else:
            yield SR(status=False,msg=f"{desc}-Failed")
