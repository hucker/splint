def filter_none():
    """All functions pass this filter"""
    return lambda _: True


def filter_all():
    return lambda _: False


def filter_tag(*tags):
    """ Filter functions by tag.  """
    return lambda function: function.tag not in tags


def filter_phase(*phases):
    """ Filter functions by phase."""
    return lambda function: function.phase not in phases


def filter_level(*levels):
    """ Filter functions by level"""
    return lambda function: function.level not in levels


def keep_all():
    return filter_none()


def keep_none():
    """ Keep no functions"""
    return filter_all()


def keep_level(*levels):
    """ Keep functions by level"""
    return lambda function: function.level in levels


def keep_phase(*phases):
    """ Keep functions by phase."""
    return lambda function: function.phase in phases


def keep_tag(*tags):
    """ Filter functions by tag.  """
    return lambda function: function.tag in tags


def and_filters(*filters):
    return lambda function: all(filter_func(function) for filter_func in filters)


def or_filters(*filters):
    return lambda function: any(filter_func(function) for filter_func in filters)


def keep_level_gt(level):
    """ Keep functions by level greater than."""
    return lambda function: function.level > level


def keep_level_gte(level):
    """ Keep functions by level greater than or equal."""
    return lambda function: function.level >= level


def keep_level_lt(level):
    """ Keep functions by level less than."""
    return lambda function: function.level < level


def keep_level_lte(level):
    """ Keep functions by level less than or equal."""
    return lambda function: function.level <= level


def filter_level_gt(level):
    """ Keep functions by level greater than."""
    return lambda function: function.level <= level


def filter_level_gte(level):
    """ Keep functions by level greater than or equal."""
    return lambda function: function.level < level


def filter_level_lt(level):
    """ Keep functions by level less than."""
    return lambda function: function.level >= level


def filter_level_lte(level):
    """ Keep functions by level less than or equal."""
    return lambda function: function.level > level


def not_filter(filter_func):
    """ Filter function that flips the sense of the fileter function"""
    return lambda function: not filter_func(function)
