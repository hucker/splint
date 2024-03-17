"""
This is the sad place for lonely functions that don't have a place
"""

def str_to_bool(s: str,default=None) -> bool:
    """ Convert a string value to a boolean."""
    s = s.strip().lower()  # Remove spaces at the beginning/end and convert to lower case

    if s in ('pass','true', 'yes', '1', 't', 'y', 'on'):
        return True
    if s in ('fail','false', 'no', '0', 'f', 'n', 'off'):
        return False

    if default is not None:
        return default

    raise ValueError(f'Cannot convert {s} to a boolean.')
