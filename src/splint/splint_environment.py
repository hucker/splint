from .splint_exception import SplintException

class SplintEnvironment:
    """
    The Splint environment is a dictionary that holds all the variables for the active environment.
    The environment is a dictionary of name/value pairs that represent the name of the environment
    variable and the scope of the variable.

    Variables that are session scope are for the duration of the session.
    Varaibles that are module scope are for the duration of the module.
    Variables that are function scope are for the duration of the function.

    This object stores the current state of the environment.

    """

    def __init__(self):
        self.environment = {}

    def __call__(self, name):
        if name not in self.environment:
            raise SplintException(f"The name {name} is not in the environment.")
        return self.environment[name]

    def add(self, name, value):
        if name in self.environment:
            raise SplintException(f"The name {name} is already in the environment.")
        self.environment[name] = value


class SPlintEnvFunctions:
    """The this has a dictionary of name/function pairs for the session."""

    def __init__(self):
        self.session = {}
        self.module = {}
        self.function = {}


    def add(self, name, scope, function):
        if name  in self.session or name in self.module or name in self.function:
            raise SplintException(f"The name {name} is already in the environment.")
        if scope == "session":
            self.session[name] = function
        elif scope == "module":
            self.module[name] = function
        elif scope == "function":
            self.function[name] = function
        else:
            raise SplintException(f"Unknown scope {scope}")