"""
Attributes can be added to any Splint function using the @attributes decorator.

Attributes allow metadata to be added to rule functions to control how they are
run, filtered, and scored. In order to meet our minimalist sensibilities, we have
kept the number of attributes to a minimum and NONE are required in order to
minimize, nearly to zero the overhead of writing a rule.

This design philosophy matches a bit of the zen of python: "Simple is better than
complex." In order to write a simple test you are never required to add each and
every attribute to a rule. Defaults are provided for all attributes. You can go
along way never using an attribute...and once you learn them you will use them all
the time.
"""
from typing import Optional, Tuple
import re
import splint

DEFAULT_TAG = ""  # A string indicating the type of rule, used for grouping/filtering results
DEFAULT_LEVEL = 1  #
DEFAULT_PHASE = ""  # A string indicating what phase of the development process a rule is best suited for
DEFAULT_WEIGHT = 100  # The nominal weight for a rule should be a positive number
DEFAULT_SKIP = False  # Set to true to skip a rule
DEFAULT_TTL_MIN = 0  # Time to live for check functions.
DEFAULT_RUID = ""
DEFAULT_FINISH_ON_FAIL=False # If a splint function yields a fail result stop processing the function
DEFAULT_SKIP_ON_NONE = False
DEFAULT_FAIL_ON_NONE = False

def _parse_ttl_string(input_string:str)->float:
    """
    Use regular expression to match a TTL string.  This pattern was a pain to figure out.  There
    are soo many permutations that need to be handled that are subtle (like the order matters in the
    list).

    Args:
        input_string (str): The input string to parse.

    Returns:
        Tuple[Optional[float], Optional[str]]: A tuple containing the parsed floating-point number
        and optional units. Returns (None, None) if no match is found.
    """
    scale = {"seconds":60,"second":60,"sec":60,"s":60,"m":1,"min":1,"minute":1,"minutes":1,"h":1/60.,"hr":1/60.,"hrs":1/60.,"hour":1/60.}
    pattern = re.compile(r"([+-]?\d+\.\d*|\d*\.\d+|[-+]?\d+)\s*(hour|hrs|hr|h|minutes|minute|min|m|seconds|second|sec|s)?")
    matches = re.findall(pattern, input_string)
    if len(matches) == 1 and len(matches[0]) == 2:
        if matches[0][1]=='':
            unit = "m"
        else:
            unit = matches[0][1]
        number = float(matches[0][0])/scale[unit]
        if number < 0.0:
            raise splint.SplintException("TTL must be greater than or equal to 0.0")
        return number


def attributes(
        *,
        tag=DEFAULT_TAG,
        phase=DEFAULT_PHASE,
        level=DEFAULT_LEVEL,
        weight=DEFAULT_WEIGHT,
        skip=DEFAULT_SKIP,
        ruid=DEFAULT_RUID,
        ttl_minutes=DEFAULT_TTL_MIN,
        finish_on_fail=DEFAULT_FINISH_ON_FAIL,
        skip_on_none=DEFAULT_SKIP_ON_NONE,
        fail_on_none=DEFAULT_FAIL_ON_NONE,

):
    """
    Decorator to add attributes to a Splint function.

    Note the *, I always forget that this means that the function is kwarg only.
    """

    # throws exception on bad input
    ttl_minutes = _parse_ttl_string(str(ttl_minutes))

    if weight <= 0:
        raise splint.SplintValueError("Weight must be greater than 0.0.  The nominal value is 100.0.")

    def decorator(func):
        func.phase = phase
        func.tag = tag
        func.level = level
        func.weight = weight
        func.skip = skip
        func.ruid = ruid
        func.ttl_minutes = ttl_minutes
        func.finish_on_fail = finish_on_fail
        func.skip_on_none = skip_on_none
        func.fail_on_none = fail_on_none
        return func

    return decorator


def get_attribute(func, attr, default_value=None):
    """
    Returns an attribute from a function.
    """
    defs = {
        "tag": DEFAULT_TAG,
        "phase": DEFAULT_PHASE,
        "level": DEFAULT_LEVEL,
        "weight": DEFAULT_WEIGHT,
        "skip": DEFAULT_SKIP,
        "ruid": DEFAULT_RUID,
        "ttl_minutes": DEFAULT_TTL_MIN,
        "finish_on_fail": DEFAULT_FINISH_ON_FAIL,
        "skip_on_none": DEFAULT_SKIP_ON_NONE,
        "fail_on_none": DEFAULT_FAIL_ON_NONE,
    }

    default = default_value or defs[attr]

    return getattr(func, attr, default)
