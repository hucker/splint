"""
This module contains splint rules that are useful for checking the status of files
on the native file system.  This functions me be removed in a future release
and replaced by functions that use the pyfilesystem package.
"""
import pathlib
import time
from typing import Generator

from .splint_exception import SplintException
from .splint_result import SR


def rule_path_exists(path_: str) -> Generator[SR, None, None]:
    """Simple rule to check for a file path."""
    if pathlib.Path(path_).exists():
        yield SR(status=True, msg=f"The path {path_} doest exist.")
    else:
        yield SR(status=False, msg=f"The path {path_} does NOT exist.")


def rule_stale_files(
        folder: str | pathlib.Path,
        pattern: str | pathlib.Path,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        no_files_pass_status: bool = True,
) -> Generator[SR, None, None]:
    """
        Rule verifies no files older than a specified age. Each too-old file is reported.
        Age defined in days, hours, minutes, and seconds.

        No files found could be deemed pass or fail. This behavior can be set, with True as default.
    """
    age_in_seconds = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
    if age_in_seconds <= 0:
        raise SplintException("Age for stale file check should be > 0")
    if age_in_seconds == 0:
        raise SplintException("Age for stale file check set to 0.  Please enter an age > 0.")

    current_time = time.time()
    count = 0
    good_count = 0
    for count, filepath in enumerate(pathlib.Path(folder).rglob(str(pattern)), start=1):
        file_mod_time = filepath.stat().st_mtime
        file_age_in_seconds = current_time - file_mod_time
        if file_age_in_seconds > age_in_seconds:
            if days > 0:
                file_age = file_age_in_seconds / 86400.0
                unit = "days"
            elif hours > 0:
                file_age = file_age_in_seconds / 3600.0
                unit = "hours"
            elif minutes > 0:
                file_age = file_age_in_seconds / 60.0
                unit = "minutes"
            else:
                file_age = file_age_in_seconds
                unit = "seconds"
            age_msg = f"age = {file_age:.2f} {unit} {age_in_seconds=}"
            yield SR(status=False, msg=f"Stale file {filepath} {age_msg}"
                     )
        else:
            good_count += 1

    # Nothing to check
    if count == 0:
        yield SR(status=no_files_pass_status,
                 msg=f"No files found matching {pattern} in {folder}.")

    # Everything OK, provide some info
    elif count == good_count:
        yield SR(status=True, msg=f"All {good_count} file(s) are not not stale.")


def rule_large_files(folder: str,
                     pattern: str,
                     max_size: float,
                     no_files_pass_status: bool = True, ):
    """
    Rule to verify that there are no files larger than a given size.
    Each file that is too big is reported.
    """
    if max_size <= 0:
        raise SplintException(f"Size for large file check should be > 0 not {max_size=}")

    count = 0
    for count, filepath in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
        size_bytes = filepath.stat().st_size
        if size_bytes > max_size:
            yield SR(
                status=False,
                msg=f"Large file {filepath}, {size_bytes} bytes, exceeds limit of {max_size} bytes",
            )
    if count == 0:
        yield SR(status=no_files_pass_status,
                 msg=f"No files found matching {pattern} in {folder}.")


def rule_max_files(folders: list, max_files: list | int, pattern: str = '*'):
    """
    Rule to verify that the number of files in a list of folders does not
    exceed a given limit.
    """

    if isinstance(folders, (str, pathlib.Path)):
        folders = [folders]
    if isinstance(max_files, int):
        max_files = [max_files] * len(folders)

    if len(folders) != len(max_files):
        raise SplintException("Number of folders and max_files must be the same.")

    for folder, max_file in zip(folders, max_files):
        count = 0
        # don't materialize the list, just count
        for count, _ in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
            pass

        if count <= max_file:
            yield SR(status=True,
                     msg=f"Folder {folder} contains less than or equal to {max_file} files.")
        else:
            yield SR(status=False,
                     msg=f"Folder {folder} contains greater than {max_file} files.")
