DEFAULT_TAG = ""
DEFAULT_LEVEL = 1
DEFAULT_PHASE = ""
DEFAULT_WEIGHT = 100
DEFAULT_SKIP = False
DEFAULT_SUID = ''


def attributes(
    *,
    tag=DEFAULT_TAG,
    phase=DEFAULT_PHASE,
    level=DEFAULT_LEVEL,
    weight=DEFAULT_WEIGHT,
    skip=DEFAULT_SKIP,
    suid=DEFAULT_SUID

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
        func.suid = suid
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
        "suid": DEFAULT_SUID
    }
    default = default_value or defs[attr]
    return getattr(func, attr, default)
