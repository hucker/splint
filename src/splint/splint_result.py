from dataclasses import dataclass,asdict
from typing import Callable, List
from collections import defaultdict
import itertools
from operator import attrgetter
from collections import Counter
@dataclass
class SplintResult:
    """
    Return value of a SplintFunction.

    Attributes:
        status (bool): Indicates if the check passed or failed. Default is False.
        module (str): The name of the module. Default is an empty string.
        function (str): The name of the function. Default is an empty string.
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
    module: str = ""
    function: str = ""
    msg: str = ""
    info_msg: str = ""
    warn_msg: str = ""
    doc: str = ""
    runtime_sec: float = 0.0
    except_: Exception = None
    traceback: str = ""
    skipped: bool = False
    tag: str = ""
    level: int = 1
    count:int = 0

    def as_dict(self):
        """Convert the SplintResult instance to a dictionary."""
        return asdict(self)


# Result transformers do one of three things, nothing and pass the result on, modify the result
# or return None to indicate that the result should be dropped.  What follows are some
# common result transformers.

def pass_only(sr:SplintResult):
    """ Return only results that have pass status"""
    return sr if sr.status else None


def fail_only(sr:SplintResult):
    """Filters out successful results.

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result if it has failed, otherwise None.
    """
    return None if sr.status else sr

def warn_as_fail(sr:SplintResult):
    """Treats results with a warning message as failures.

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result with its status set to False if there's a warning message.
    """
    if sr.warn_msg:
        sr.status = False
    return sr

def fix_blank_msg(sr:SplintResult):
    """Sets the message to the module and function name if it's blank.

    Args:
        sr (SplintResult): The result to check.

    Returns:
        SplintResult: The result with its message set to the module and function name if it was blank.
    """
    if not sr.msg:
        sr.msg = f"{sr.module}.{sr.function}"
    return sr

def yield_result_pipeline(transformers: List[Callable], results:List[SplintResult]):
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

def result_pipeline(transformers:List[Callable], results:List[SplintResult]):
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

def results_as_dict(results:List[SplintResult]):
    """Converts a list of SplintResult to a list of dictionaries.

    Args:
        results (List[SplintResult]): The list of results to convert.

    Returns:
        List[Dict]: The list of dictionaries.
    """
    return [result.as_dict() for result in results]



def group_by(results:List[SplintResult], keys:List[str]):
    """
    Groups a list of SplintResult by a list of keys.

    This funciton allows for arbitrary grouping of SplintResult using the keys of the
    SplintResult as the grouping criteria.  You can group in any order or depth with
    any number of keys.

    Args:
        results (List[SplintResult]): The list of results to group.
        keys (List[str]): The list of keys to group by.

    """

    if not keys:
        return results

    key = keys[0]
    key_func = attrgetter(key)

    # Check if all objects have the required attribute
    if not all(hasattr(x, key) for x in results):
        raise ValueError(f"All objects must have an attribute '{key}'")

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