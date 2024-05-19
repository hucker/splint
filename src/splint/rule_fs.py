"""
Set of baseline rules that uses the pyfilesystem module to OS-agnostic checks on things
about the file system, file existing, age etc.
"""
import datetime as dt
import fnmatch
from typing import List

from fs.base import FS
from fs.errors import FSError

from .splint_result import SR


def rule_fs_paths_exist(fs_obj: FS, paths: List[str]) -> bool:
    """ Check a bunch of paths."""
    for path in paths:
        yield from rule_fs_path_exists(fs_obj, path)


def rule_fs_path_exists(fs_obj: FS, path_: str) -> bool:
    """Simple rule to check for a file path."""
    yield SR(status=fs_obj.exists(path_), msg=f"The path {path_} on {fs_obj.root_path} exists.")


def human_readable_size(size_in_bytes: int):
    """
    Convert a given size in bytes to a human-readable string format.

    Parameters:
    size_in_bytes (int): The size in bytes to convert.

    Returns:
    string: The size in bytes, converted to a human-readable format
    (e.g. 'bytes', 'KB', 'MB', 'GB', 'TB', 'PB'). The result is
    rounded to the nearest tenth if it is not in bytes. If the original
    size was negative, the result is also negative.
    """
    units = ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB']
    index = 0

    # Convert negative bytes to positive, and remember if it was negative.
    is_negative = size_in_bytes < 0
    size_in_bytes = abs(size_in_bytes)

    while size_in_bytes >= 2048 and index < len(units) - 1:  # 2048 switch to the next unit at 2.00 exactly
        size_in_bytes /= 1024
        index += 1

    # If the size_in_bytes was negative, switch it back to negative.
    size_in_bytes = -size_in_bytes if is_negative else size_in_bytes

    # Special case for bytes (no decimal point is needed)
    if units[index] == 'bytes':
        # Special case for 1 byte (singular)
        if abs(size_in_bytes) == 1:
            return f"{size_in_bytes} byte"

        # Other cases for bytes (plural)
        return f"{int(size_in_bytes)} bytes"

    # General case
    return f"{size_in_bytes:.1f} {units[index]}"


def rule_fs_file_within_max_size(filesys: FS, path: str, max_file_size: int, skip_if_missing=False):
    """Check if a file exists and its size is within the given max_file_size limit"""
    if not filesys.isfile(path):
        yield SR(status=False, msg=f'File "{path}" does not exist in {filesys.root_path}', skipped=skip_if_missing)
    else:
        file_size = filesys.getsize(path)
        file_size_str = human_readable_size(file_size)
        delta = file_size - max_file_size
        # delta_str = human_readable_size(abs(delta))
        if delta < 0:
            yield SR(status=False, msg=f'File "{path}" size={file_size_str} exceeds size limit by -{delta} bytes.')
        else:
            yield SR(status=True, msg=f'File "{path}" size={file_size_str} within size limit by {delta} bytes.')


def sec_format(seconds):
    """
    Convert a given time in seconds to a string expressing the time in a more
    human-readable format.  Of note when calculating months it uses 30-day months which is fine
    for a few months but at 23 months it has 10 days of error.

    Time is rounded down in the largest time units possible (days, hours, minutes, then seconds)
    For time less than 2 days, it's represented in hours. For less than 2 hours, it's in minutes.
    For less than 2 minutes, it's in seconds. The seconds are displayed with up to three
    digits of precision.

    NOTE: Months are problematic since they aren't constantly sized (same with years), I'm banking
          on this being human-readable and that very slight errors  in the last decimal point
          are a problem.

    Parameters:
    seconds (float): The time duration in seconds.

    Returns:
    string: A string representation of the provided time duration making it easier to read.

    """
    seconds_per_minute = 60
    seconds_per_hour = 60 * seconds_per_minute
    seconds_per_day = 24 * seconds_per_hour
    seconds_per_month = 30 * seconds_per_day  # Human-readable, don't whine about this
    seconds_per_year = 365 * seconds_per_day

    # Check if seconds is very small negative, if yes then round it to 0
    if -0.001 < seconds < 0:
        seconds = 0

    # Store the original sign and use absolute value for calculations.
    sign = '-' if seconds < 0 else ''
    seconds = round(abs(seconds), 3)

    if seconds == 0:
        sign = ''

    # Order of items matters, biggest goes first
    time_units = [
        ("years", seconds_per_year),
        ("months", seconds_per_month),
        ("days", seconds_per_day),
        ("hours", seconds_per_hour),
        ("minutes", seconds_per_minute)
    ]

    for unit, sec_in_unit in time_units:
        if seconds >= 2 * sec_in_unit:
            return f"{sign}{seconds / sec_in_unit:.1f} {unit}"

    # Seconds are special case. For small seconds we report to
    # extra precision since we assume that we are dealing with
    # times on a human scale rather than on micro scales.
    if seconds >= 2:
        return f"{sign}{seconds:.1f} seconds"

    if seconds == 0:
        return "0.000 seconds"  # no sign

    return f'{sign}{seconds:.3f} seconds'


def rule_fs_oldest_file_age(filesys: FS, max_age_minutes: float = 0,
                            max_age_hours: float = 0,
                            max_age_days: float = 0,
                            max_age_seconds: float = 0,
                            patterns=None,
                            no_files_stat=True,
                            no_files_skip=True,
                            now_: dt.datetime = None):
    """
    This rule is useful for ensuring that files are being removed in
    a timely manner as in the case where a folder is used to queue up
    data files that are processed.  Old files indicates an issue.
    """
    patterns = patterns or ['*']

    if isinstance(patterns, str):
        patterns = patterns.split(',')

    now = (now_ or dt.datetime.utcnow()).replace(tzinfo=dt.timezone.utc)
    max_file_age_seconds = dt.timedelta(days=max_age_days,
                                        hours=max_age_hours,
                                        minutes=max_age_minutes,
                                        seconds=max_age_seconds).total_seconds()

    try:
        files = filesys.listdir('/')
        files = [f for f in files if
                 filesys.isfile(f) and any(
                     fnmatch.fnmatch(f, pattern) for pattern in patterns)]
    except FSError as e:
        yield SR(status=False, msg=f"Error during listing files: {str(e)}", except_=e)
        return

    if not files:
        yield SR(status=no_files_stat,
                 msg=f"No files found in the directory: {filesys.getsyspath('/')}",
                 skipped=no_files_skip)
        return

    try:
        oldest_file = min(files, key=lambda f: filesys.getinfo(f, namespaces=['details']).modified)
        oldest_file_modified = filesys.getinfo(oldest_file, namespaces=['details']).modified
        oldest_file_age_seconds = (now - oldest_file_modified).total_seconds()
    except FSError as e:
        yield SR(status=False, msg=f"Error during checking file's age: {str(e)}", except_=e)
        return

    time_str = sec_format(max_file_age_seconds)
    old_str = sec_format(oldest_file_age_seconds)

    if oldest_file_age_seconds <= max_file_age_seconds:
        yield SR(status=True,
                 msg=f'Oldest file "{oldest_file}" is within age limit of {time_str}. File age= {old_str}')
    else:
        yield SR(status=False,
                 msg=f'Oldest file "{oldest_file}" is more than {time_str}. File age= {old_str}')

# def rule_fs_youngest_file_age(filesys: FS, min_age_minutes: float = 0, min_age_hours: float = 0,
#                               min_age_days: float = 0, min_age_seconds: float = 0,
#                               patterns=None, no_files_status=True,
#                               now_: dt.datetime = None):
#     """ UNTESTED """
#
#
#     patterns = patterns or ['*']
#
#     if isinstance(patterns, str):
#         patterns = patterns.split(',')
#
#     now = (now_ or dt.datetime.utcnow()).replace(tzinfo=dt.timezone.utc)
#     min_file_age_seconds = dt.timedelta(days=min_age_days, hours=min_age_hours,
#                                         minutes=min_age_minutes,
#                                         seconds=min_age_seconds).total_seconds()
#
#     try:
#         files = filesys.listdir('/')
#         files = [f for f in files if
#                  filesys.isfile(f) and any(
#                      fnmatch.fnmatch(f, pattern) for pattern in patterns)]
#     except FSError as e:
#         yield SR(status=False, msg=f"Error during listing files: {str(e)}", except_=e)
#         return
#
#     if not files:
#         yield SR(status=no_files_status,
#                  msg=f"No files found in the directory: {filesys.getsyspath('/')}")
#         return
#
#     try:
#         youngest_file = max(files, key=lambda f: filesys.getinfo(f, namespaces=['details']).modified)
#         youngest_file_modified = filesys.getinfo(youngest_file, namespaces=['details']).modified
#         youngest_file_age_seconds = (now - youngest_file_modified).total_seconds()
#     except FSError as e:
#         yield SR(status=False, msg=f"Error during checking file's age: {str(e)}", except_=e)
#         return
#
#     time_str = sec_format(min_file_age_seconds)
#     young_str = sec_format(youngest_file_age_seconds)
#
#     if youngest_file_age_seconds >= min_file_age_seconds:
#         yield SR(status=True,
#           msg=f'Youngest file "{youngest_file}" is more than minimal permitted age of {time_str}. The age of the file is {young_str}')
#     else:
#         yield SR(status=False,
#                  msg=f'Youngest file "{youngest_file}" is less than minimal permitted age of {time_str}. The age of the file is {young_str}')
