""" This module contains the SplintResult class and some common result transformers. """

import itertools
import traceback
from collections import Counter
from dataclasses import asdict, dataclass, field
from operator import attrgetter
from typing import List

from .splint_exception import SplintException


@dataclass
class SplintResult:
    """
    Return value of a SplintFunction.

    This dataclass tracks the status of a SplintFunction. It includes data relating to the function
    call, such as the status, module name, function name, message, additional info, warning message,
    docstring, runtime, exceptions, traceback, skip flag, tag, level, and count.

    This data can be used for reporting purposes.

    Attributes:
        status (bool): Check status. Default is False.
        module_name (str): Module name. Default is "".
        func_name (str): Function name. Default is "".
        msg (str): Message to the user. Default is "".
        info_msg (str): Additional function call info. Default is "".
        warn_msg (str): Warning message. Default is "".
        doc (str): Function docstring. Default is "".
        runtime_sec (float): Function runtime in seconds. Default is 0.0.
        except_ (Exception): Raised exception, if any. Default is None.
        traceback (str): Exception traceback, if any. Default is "".
        skipped (bool): Function skip flag. Default is False.
        tag (str): Function tag. Default is "".
        level (int): Function level. Default is 1.
        count (int): Return value count from a SplintFunction.
        """

    status: bool | None = False

    # Name hierarchy
    func_name: str = ""
    pkg_name: str = ""
    module_name: str = ""

    # Msg Hierarchy
    msg: str = ""
    info_msg: str = ""
    warn_msg: str = ""

    # Function Info
    doc: str = ""

    # Timing Info
    runtime_sec: float = 0.0

    # Error Info
    except_: Exception = None
    traceback: str = ""
    skipped: bool = False

    weight: float = 100.0

    # Attribute Info - This needs to be factored out?
    tag: str = ""
    level: int = 1
    phase: str = ""
    count: int = 0
    ruid: str = ""
    ttl_minutes: float = 0.0

    # Mitigations
    mit_msg: str = ""
    owner_list: List[str] = field(default_factory=list)

    # Bad parameters
    skip_on_none: bool = False
    fail_on_none: bool = False

    def __post_init__(self):
        # Automatically grab the traceback for better debugging.
        if self.except_ is not None and not self.traceback:
            self.traceback = traceback.format_exc()

    def as_dict(self):
        """Convert the SplintResult instance to a dictionary."""
        d = asdict(self)
        d['except_'] = str(d['except_'])
        return d


# Shorthand
SR = SplintResult


class SplintYield:
    """
    This allows syntactic sugar to know how many times a generator
    has been fired and how many passes and fails have occurred.

    These internal counts allow top level code to NOT manage that
    state at the rule level.  Instead, you just report your passes

    and fails and ask at the end how it played out.

    gen = SprintYield()

    if cond:
        yield from gen(SR(True,"Info...")
    if not gen.yielded:
        yield from gen(SR(False,"Nothing to do"))

    """

    def __init__(self):
        self._count = 0
        self._fail_count = 0

    @property
    def yielded(self):
        """ Have we yielded once?"""
        return self._count > 0

    @property
    def count(self):
        """How many times have we yielded?"""
        return self._count

    @property
    def fail_count(self):
        """How many fails have there been"""
        return self._fail_count

    @property
    def pass_count(self):
        """How many passes have there been"""
        return self.count - self._fail_count

    @property
    def counts(self):
        """Return pass/fail/total yield counts"""
        return self.pass_count, self.fail_count, self.count

    def __call__(self, results: SplintResult | List[SplintResult], fail_only: bool = False):

        if isinstance(results, SplintResult):
            results = [results]
        # elif isinstance(results, list) and isinstance(results[0], SplintResult):
        #    pass
        else:
            raise SplintException(f"Unknown result type {type(results)}")
        for result in results:
            self._count += 1
            self._fail_count += 0 if result.status else 1
            yield result


# Result transformers do one of three things, nothing and pass the result on, modify the result
# or return None to indicate that the result should be dropped.  What follows are some
# common result transformers.

def passes_only(sr: SplintResult):
    """ Return only results that have pass status"""
    return sr if sr.status else None


def fails_only(sr: SplintResult):
    """Filters out successful results.

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result if it has failed, otherwise None.
    """
    return None if sr.status else sr


def remove_info(sr: SplintResult):
    """Filter out messages tagged as informational

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result if it has failed, otherwise None.
    """
    return None if sr.info_msg else sr


def warn_as_fail(sr: SplintResult):
    """Treats results with a warning message as failures.

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result with its status set to False if there's a warning message.
    """
    if sr.warn_msg:
        sr.status = False
    return sr


def results_as_dict(results: List[SplintResult]):
    """Converts a list of SplintResult to a list of dictionaries.

    Args:
        results (List[SplintResult]): The list of results to convert.

    Returns:
        List[Dict]: The list of dictionaries.
    """
    return [result.as_dict() for result in results]


def group_by(results: List[SplintResult], keys: List[str]):
    """
    Groups a list of SplintResult by a list of keys.

    This function allows for arbitrary grouping of SplintResult using the keys of the
    SplintResult as the grouping criteria.  You can group in any order or depth with
    any number of keys.

    Args:
        results (List[SplintResult]): The list of results to group.
        keys (List[str]): The list of keys to group by.S

    """

    if not keys:
        raise SplintException("Empty key list for grouping results.")

    key = keys[0]
    key_func = attrgetter(key)

    # I do not believe this is an actual test case as it would require a bug in
    # the code.  I'm leaving it here for now.
    # if not all(hasattr(x, key) for x in results):
    #    raise splint.SplintValueError(f"All objects must have an attribute '{key}'")

    # Sort and group by the first key
    results = sorted(results, key=key_func)
    results = [(k, list(g)) for k, g in itertools.groupby(results, key=key_func)]

    # Recursively group by the remaining keys
    if len(keys) > 1:
        for i, (k, group) in enumerate(results):
            results[i] = (k, group_by(group, keys[1:]))

    return dict(results)


def overview(results: List[SplintResult]) -> str:
    """
    Returns an overview of the results.

    Args:
        results (List[SplintResult]): The list of results to summarize.

    Returns:
        str: A summary of the results.
    """

    result_counter = Counter(
        'skip' if result.skipped else
        'error' if result.except_ else
        'fail' if not result.status else
        'warn' if result.warn_msg else
        'pass'
        for result in results
    )

    total = len(results)
    passed = result_counter['pass']
    failed = result_counter['fail']
    errors = result_counter['error']
    skipped = result_counter['skip']
    warned = result_counter['warn']

    return f"Total: {total}, Passed: {passed}, Failed: {failed}, " \
           f"Errors: {errors}, Skipped: {skipped}, Warned: {warned}"
