import pathlib
import requests
import time

from .splint_exception import SplintException
from .splint_result import SplintResult as SR


def rule_path_exists(path_: str) -> bool:
    """Simple rule to check for a file path."""
    yield SR(status=pathlib.Path(path_).exists(), msg=f"The path {path_} exists.")


def rule_stale_files(
    folder: str,
    pattern: str,
    days: float = 0,
    hours: float = 0,
    minutes: float = 0,
    seconds: float = 0,
    fail_only=True,
):
    """Rule to verify that there are no files older than some age.  Each file that is too old is reported.  The age is specified in days, hours, minutes, and seconds."""
    age_in_seconds = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
    if age_in_seconds <= 0:
        raise SplintException("Age for stale file check should be > 0")

    current_time = time.time()
    count = 0
    for count, filepath in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
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
            yield SR(
                status=False, msg=f"Stale file {filepath} age = {file_age:.2f} {unit} {age_in_seconds=}"
            )
    if count == 0 and not fail_only:
        yield SR(status=True, msg=f"No files found matching {pattern} in {folder}.")


def rule_large_files(folder: str, pattern: str, max_size: float, fail_only=True):
    """Rule to verify that there are no files larger than a given size.  Each file that is too big is reported."""
    if max_size <= 0:
        raise SplintException("Size for large file check should be > 0")

    count = 0
    for count, filepath in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
        file_size_in_bytes = filepath.stat().st_size
        if file_size_in_bytes > max_size:
            yield SR(
                status=False,
                msg=f"Large file {filepath} size = {file_size_in_bytes} bytes, exceeds limit of {max_size} bytes",
            )
    if count == 0 and not fail_only:
        yield SR(status=True, msg=f"No files found matching {pattern} in {folder}.")


def rule_max_files(folders: list, max_files: int, pattern: str = '*', fail_only=True):
    """Rule to verify that the number of files in a list of folders does not exceed a given limit."""

    if isinstance(max_files,int):
        max_files = [max_files]*len(folders)

    if len(folders) != len(max_files):
        raise SplintException("The number of folders and the number of max_files must be the same.")

    for folder,max_file in zip(folders,max_files):
        count = 0
        for count, _ in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
            pass

        if count > max_file:
                yield SR(status=False, msg=f"Folder {folder} contains more than {max_file} files.")
        if fail_only is False:
            yield SR(status=True, msg=f"Folder {folder} contains less than {max_file} files. ({count=}) ")

