class SplintTypeError(TypeError):
    """Type errors associated with setting up Splint

    When bad types are sent to splint, this exception will be raised and should
    not be confused the TypeError that (should) indicate an unexpected lower
    level error.

    """
    pass


class SplintValueError(ValueError):
    """ Value Error associated with setting up Splint

    These exceptions will occur when setting up parameters on splint attributes and
    basic setup.  For example a negative weight.

    """



class SplintTypeError(TypeError):
    """Type errors associated with setting up Splint

    When bad types are sent to splint, this exception will be raised and should
    not be confused the TypeError that (should) indicate an unexpected lower
    level error.

    """
    pass

class SplintValueError(ValueError):
    """ Value Error associated with setting up Splint

    These exceptions will occur when setting up parameters on splint attributes and
    basic setup.  For example a negative weight.

    """

class SplintException(Exception):
    """Specialized exception for splint."""
    pass
