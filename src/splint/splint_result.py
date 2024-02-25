""" This module contains the SplintResult class and some common result transformers. """

import itertools
from collections import Counter
from dataclasses import asdict, dataclass, field
from operator import attrgetter
from typing import Callable, List

import splint


@dataclass
class SplintResult:
    """
    Return value of a SplintFunction.

    This dataclass tracks the result of a SplintFunction. It contains information about the function call, including
    the status, the name of the module and function, a message, additional information, a warning message, the docstring,
    the runtime, any exceptions raised, the traceback, whether the function was skipped, a tag, a level, and a count.

    This data can be used for reporting purposes.

    Attributes:
        status (bool): Indicates if the check passed or failed. Default is False.
        module_name (str): The name of the module. Default is an empty string.
        func_name (str): The name of the function. Default is an empty string.
        msg (str): A short one-line message to be displayed to the user. Default is an empty string.
        info_msg (str): Additional information about the function call. Default is an empty string.
        warn_msg (str): A warning message. Default is an empty string.
        doc (str): The docstring of the function. Default is an empty string.
        runtime_sec (float): The runtime of the function in seconds. Default is 0.0.
        except_ (Exception): The exception raised by the function, if any. Default is None.
        traceback (str): The traceback of the exception, if any. Default is an empty string.
        skipped (bool): Indicates if the function was skipped. Default is False.
        tag (str): A tag for the function. Default is an empty string.
        level (int): The level of the function. Default is 1.
        count (int): This is the index the counts the number of return values from a SplintFunction.
    """

    status: bool = False

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

    def as_dict(self):
        """Convert the SplintResult instance to a dictionary."""
        d = asdict(self)
        d['except_'] = str(d['except_'])
        return d


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
        return self._count > 0

    @property
    def count(self):
        return self._count

    @property
    def fail_count(self):
        return self._fail_count

    @property
    def pass_count(self):
        return self.count - self._fail_count

    @property
    def counts(self):
        """Return pass/fail/total yield counts"""
        return self.pass_count, self.fail_count, self.count

    def __call__(self, results: SplintResult | List[SplintResult], fail_only: bool = False):

        if isinstance(results, SplintResult):
            results = [results]
        elif isinstance(results, list) and isinstance(results[0], SplintResult):
            pass
        else:
            raise splint.SplintException(f"Unknown result type {type(results)}")
        for result in results:
            self._count += 1
            self._fail_count += 0 if result.status else 1
            yield result


# Result transformers do one of three things, nothing and pass the result on, modify the result
# or return None to indicate that the result should be dropped.  What follows are some
# common result transformers.

def pass_only(sr: SplintResult):
    """ Return only results that have pass status"""
    return sr if sr.status else None


def fail_only(sr: SplintResult):
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


def fix_blank_msg(sr: SplintResult):
    """Sets the message to the module and function name if it's blank.

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result with its message set to the module and function name if it was blank.
    """
    pkg_msg = f"{sr.pkg_name}." if sr.pkg_name else ""
    mod_msg = f"{sr.module_name}." if sr.module_name else ""
    func_msg = f"{sr.func_name}." if sr.func_name else ""

    if not sr.msg:
        sr.msg = f"{pkg_msg}{mod_msg}{func_msg}.{sr.count:03d}"
    return sr


def yield_result_pipeline(transformers: List[Callable], results: List[SplintResult]):
    """Applies a list of functions to a list of results.

    The functions are applied in order and the results are passed to the next function in the list.

    Args:
        transformers (List[Callable]): The list of functions to apply.
        results (List[SplintResult]): The list of results to transform.

    Yields:
        SplintResult: The transformed results, unless dropped by a transformer.

    Example:
        results = yield_result_pipeline([pass_only,fix_blank_msg], results)
    """

    for result in results:
        for transformer in transformers:
            result = transformer(result)
            # None means drop the result
            if result is None:
                break
        if result is not None:
            yield result


def result_pipeline(transformers: List[Callable], results: List[SplintResult]):
    """Applies a list of functions to a list of results and returns a list.

    This is a list version of the yield_result_pipeline function. It returns a list of results
    that may be more convenient in some cases.

    Args:
        transformers (List[Callable]): The list of functions to apply.
        results (List[SplintResult]): The list of results to transform.

    Returns:
        List[SplintResult]: The list of transformed results, unless dropped by a transformer.
    """
    return list(yield_result_pipeline(transformers, results))


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
        return results

    key = keys[0]
    key_func = attrgetter(key)

    # Check if all objects have the required attribute
    if not all(hasattr(x, key) for x in results):
        raise splint.SplintValueError(f"All objects must have an attribute '{key}'")

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

    return f"Total: {total}, Passed: {passed}, Failed: {failed}, Errors: {errors}, Skipped: {skipped}, Warned: {warned}"
