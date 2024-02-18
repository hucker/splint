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
import splint

DEFAULT_TAG = ""       # A string indicating the type of rule, used for grouping/filtering results
DEFAULT_LEVEL = 1      #
DEFAULT_PHASE = ""     # A string indicating what phase of the development process a rule is best suited for
DEFAULT_WEIGHT = 100   # The nominal weight for a rule should be a positive number
DEFAULT_SKIP = False   # Set to true to skip a rule
DEFAULT_RUID = ""


def attributes(
    *,
    tag=DEFAULT_TAG,
    phase=DEFAULT_PHASE,
    level=DEFAULT_LEVEL,
    weight=DEFAULT_WEIGHT,
    skip=DEFAULT_SKIP,
    ruid=DEFAULT_RUID
):
    """
    Decorator to add attributes to a Splint function..
    """

    def decorator(func):
        func.phase = phase
        func.tag = tag
        func.level = level
        func.weight = weight
        func.skip = skip
        func.ruid = ruid
        return func

    if weight <= 0:
        raise splint.SplintValueError("Weight must be greater than 0.0.  The nominal value is 100.0.")

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
    }

    default = default_value or defs[attr]

    return getattr(func, attr, default)
