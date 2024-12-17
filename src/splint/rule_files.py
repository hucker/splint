"""
This module contains splint rules that are useful for checking the status of files
on the native file system.  This functions me be removed in a future release
and replaced by functions that use the pyfilesystem package.
"""
import pathlib
import time
from typing import Generator

from .splint_exception import SplintException
from .splint_format import SM
from .splint_result import SR, SplintYield,SplintResult


def rule_path_exists(path_: str) -> Generator[SR, None, None]:
    """Simple rule to check for a file path."""
    path_str = SM.code(path_)
    try:
        if pathlib.Path(path_).exists():
            yield SR(status=True, msg=f"The path {SM.code(path_str)} does exist.")
        else:
            yield SR(status=False, msg=f"The path  {SM.code(path_str)} does {SM.bold('NOT')} exist.")
    except (FileNotFoundError, PermissionError,IOError) as e:
        yield SR(status=False, 
                 msg="Exception occurred while checking for the path {SM.code(path_str)}",
                 except_=e)

def rule_paths_exist(paths:list[str]|str,
                     summary_only=False,
                     summary_name=None,
                     name = "Path Check",
                     no_paths_pass_status=False)->Generator[SR, None, None]:
    y=SplintYield(summary_only=summary_only,summary_name=summary_name)
    
    if isinstance(paths, str):
        paths = paths.split(" ")
    
    for path in paths:
        yield from y(rule_path_exists(path))
    
    if y.count == 0:
        yield from y(status=no_paths_pass_status,
                     msg=f"There were no paths to check in {SM.code(name)}.")

    if summary_only:
        yield from y.yield_summary()


def rule_stale_file(
        filepath: pathlib.Path,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        current_time = None
) ->SplintResult:
    """Check a single file for being stale."""

    current_time = current_time or time.time()

    age_in_seconds = days * 86400.0 + hours * 3600.0 + minutes * 60.0 + seconds
    if age_in_seconds <= 0:
        raise SplintException(f"Age for stale file check {SM.code(age_in_seconds)} should be > 0")
    
    try:
        file_mod_time = filepath.stat().st_mtime
        file_age_in_seconds = current_time - file_mod_time
    
        if file_age_in_seconds > age_in_seconds:
            unit = "seconds"
            if days > 0:
                file_age = file_age_in_seconds / 86400.0
                unit = "days"
            elif hours > 0:
                file_age = file_age_in_seconds / 3600.0
                unit = "hours"
            elif minutes > 0:
                file_age = file_age_in_seconds / 60.0
                unit = "minutes"
            elif seconds > 0:
                file_age = file_age_in_seconds
            else:
                raise SplintException("No file age times were specified.")
            age_msg = f"age = {file_age:.2f} {unit} {age_in_seconds=}"
            yield SR(status=False, msg=f"Stale file {SM.code(filepath)} {SM.code(age_msg)}")
        else:
            yield SR(status=True, msg=f"Not stale file {SM.code(filepath)}")
    except (FileNotFoundError, PermissionError,IOError) as exc:
        yield SR(status=False, 
                 msg="Exception occurred while checking for the path {SM.code(path_str)}", 
                 except_=exc)


def rule_stale_files(
        folder: str | pathlib.Path,
        pattern: str | pathlib.Path,
        days: float = 0,
        hours: float = 0,
        minutes: float = 0,
        seconds: float = 0,
        no_files_pass_status: bool = True,
        summary_only=False,
        summary_name=None
) -> Generator[SR, None, None]:
    """
        Rule verifies no files older than a specified age. Each too-old file is reported.
        Age defined in days, hours, minutes, and seconds.

        No files found could be deemed pass or fail. This behavior can be set, with True as default.
    """
    y = SplintYield(summary_only=summary_only, summary_name=summary_name or "Rule_stale_files")


    current_time = time.time()
    for filepath in pathlib.Path(folder).rglob(str(pattern)):
        yield from y.results(rule_stale_file(filepath=filepath,
                                     days=days,
                                     hours=hours,
                                     minutes=minutes,
                                     seconds=seconds,
                                     current_time=current_time))
        
    if y.count == 0:
        yield from y(status=no_files_pass_status,
                     msg=f"No files were found in {SM.code(folder)} matching pattern {SM.code(folder)}")

    if summary_only:
        yield from y.yield_summary()


def rule_large_files(folder: str,
                     pattern: str,
                     max_size: float,
                     no_files_pass_status: bool = True,
                     summary_only=False,
                     summary_name=None):
    """
    Rule to verify that there are no files larger than a given size.
    Each file that is too big is reported.
    """

    y = SplintYield(summary_only=summary_only, summary_name=summary_name or "Rule_large_files")

    if max_size <= 0:
        raise SplintException(f"Size for large file check should be > 0 not {max_size=}")

    for filepath in pathlib.Path(folder).rglob(pattern):
        size_bytes = filepath.stat().st_size
        if size_bytes > max_size:
            yield from y(
                status=False,
                msg=f"Large file {SM.code(filepath)}, {SM.code(size_bytes)} bytes, exceeds limit of {SM.code(max_size)} bytes",
            )
    if y.count == 0:
        yield from y(status=no_files_pass_status,
                     msg=f"No files found matching {SM.code(pattern)} in {SM.code(folder)}.")

    if summary_only:
        yield from y.yield_summary()


def rule_max_files(folders: list,
                   max_files: list | int,
                   pattern: str = '*',
                   summary_only=False,
                   summary_name=None):
    """
    Rule to verify that the number of files in a list of folders does not
    exceed a given limit.
    """
    y = SplintYield(summary_only=summary_only, summary_name=summary_name or "Rule_max_files")

    if isinstance(folders, (str, pathlib.Path)):
        folders = [folders]
    if isinstance(max_files, int):
        max_files = [max_files] * len(folders)

    if len(folders) != len(max_files):
        raise SplintException(f"Number of folders and max_files {max_files} must be the same.")

    for folder, max_file in zip(folders, max_files):
        count = 0
        # don't materialize the list, just count
        for count, _ in enumerate(pathlib.Path(folder).rglob(pattern), start=1):
            pass

        if count <= max_file:
            yield from y(status=True,
                         msg=f"Folder {SM.code(folder)} contains less than or equal to {SM.code(max_file)} files.")
        else:
            yield from y(status=False,
                         msg=f"Folder {SM.code(folder)} contains greater than {SM.code(max_file)} files.")

    if summary_only:
        yield from y.yield_summary()
