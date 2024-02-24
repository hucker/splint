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

import splint

DEFAULT_TAG = ""  # A string indicating the type of rule, used for grouping/filtering results
DEFAULT_LEVEL = 1  #
DEFAULT_PHASE = ""  # A string indicating what phase of the development process a rule is best suited for
DEFAULT_WEIGHT = 100  # The nominal weight for a rule should be a positive number
DEFAULT_SKIP = False  # Set to true to skip a rule
DEFAULT_TTL_MIN = 0  # Time to live for check functions.
DEFAULT_RUID = ""


def _parse_ttl_string(input_string: str) -> Tuple[Optional[float], Optional[str]]:
    """
    Parses a string containing a floating-point number followed by optional units.

    Args:
        input_string (str): The input string to parse.

    Returns:
        Tuple[Optional[float], Optional[str]]: A tuple containing the parsed floating-point number
        and optional units. Returns (None, None) if no match is found.
    """
    units = " sec,1 second,1 min,60 minute,60 h,3600 hr,3600 hour,3600 hrs,3600 s,1 m,60"
    d = {}
    for pair in units.split():
        key, value = pair.split(",")
        d[key] = float(value)

    # Drop through no units
    scale = 60.0
    for key, value in d.items():
        if input_string.endswith(key):
            scale = value
            input_string = input_string[:-len(key)]
            break

    minutes = float(input_string) * scale / 60.0

    if minutes < 0.0:
        raise splint.SplintException("TTL must be greater than or equal to 0.0")

    return minutes


def attributes(
        *,
        tag=DEFAULT_TAG,
        phase=DEFAULT_PHASE,
        level=DEFAULT_LEVEL,
        weight=DEFAULT_WEIGHT,
        skip=DEFAULT_SKIP,
        ruid=DEFAULT_RUID,
        ttl_minutes=DEFAULT_TTL_MIN,

):
    """
    Decorator to add attributes to a Splint function.
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
    }

    default = default_value or defs[attr]

    return getattr(func, attr, default)
