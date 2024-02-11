DEFAULT_TAG = ""
DEFAULT_LEVEL = 1
DEFAULT_PHASE = ""
DEFAULT_WEIGHT = 100
DEFAULT_SKIP = False
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
        raise ValueError("Weight must be greater than 0.0.  The nominal value is 100.0.")

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
