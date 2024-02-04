from .splint_exception import SplintException
import dataclasses
from typing import Callable,Any
import inspect
import sys
from enum import Enum


PANDAS_AVAILABLE = 'pandas' in sys.modules

if PANDAS_AVAILABLE:
    import pandas


POLARS_AVAILABLE = 'polars' in sys.modules
if POLARS_AVAILABLE:
    import polars


def make_constant_function(name, constant_value):
    """
    This is a way to allow the user to provide a dictionary
    of values to the environment.  That converts them
    all to functions that return the value.  Doing so allows
    dealing with environment variables  all in the same way,
    the result of calling a function.

    Args:
        name (str): Variable name of function
        constant_value (Any): Value to return.
    """
    def func():
        return constant_value
    func.__name__ = name
    return func

class SplintEnvScope(Enum):
    """ Indicate the level that each environment variable is valid.

        Note: print using .name or .value

    """
    REPO = 4
    PACKAGE = 3
    MODULE = 2
    FUNCTION = 1

@dataclasses.dataclass
class SplintEnvFunction:
    """Handle individual environment functions

    Keep track of state and handle setup and teardown for generator base
    environment functions and just extracting a value for non generators."""
    name: str
    scope: SplintEnvScope
    function: Callable[...,Any]
    value: any = None
    ready:bool = False       # You must have ready true to use the value since a valid value for value is None!!
    force_immutable: bool = True

    # Tracking internal state.
    iterator = None

    def setup(self,scope):
        """
        Set the value of the function if it is at the given scope.

        The intent of this is that there will be a large list of environment functions
        all at different levels and we can set them all by passing in the scope as
        needed.

        Note that we are VERY careful with immutable data structures.  We don't want
        to accidentally change the value of a function that is at a higher scope. Everybody
        gets a clean copy.

        Note that we handle data frames here as mutable data, and return a copy each time
        it is setup.

        """
        if self.scope.value <= scope.value:
            if inspect.isgeneratorfunction(self.function):
                # Setup
                self.iterator = self.function()
                self.value = next(self.iterator)
            else:
                self.value = self.function()

            if self.force_immutable:
                if isinstance(self.value,list):
                    self.value = self.value.copy()
                if isinstance(self.value,dict):
                    self.value = self.value.copy()
                if isinstance(self.value,set):
                    self.value = self.value.copy()

                # Check if pandas is available and if the value is a DataFrame
                if PANDAS_AVAILABLE and isinstance(self.value, pandas.DataFrame):
                    self.value = self.value.copy()
                if POLARS_AVAILABLE and isinstance(self.value, polars.DataFrame):
                    self.value = self.value.clone()
            self.ready = True

    def teardown(self,scope):
        """
        Clear the value of the function if it is at the given scope.

        The intent of this is that there will be a large list of environment functions
        all at different levels and we can clear them all by passing in the scope as
        needed
        """
        if self.scope.value <= scope.value:
            if inspect.isgeneratorfunction(self.function):
                # Teardown
                next(self.iterator,SplintEnvScope.FUNCTION)

        self.value = None
        self.ready = False



class SplintEnvironment:
    """
    The Splint environment is a dictionary that holds all the variables for the active environment.
    The environment is a dictionary of name/value pairs that represent the name of the environment
    variable and the scope of the variable.

    Variables that are repo scope are for the duration of the run.
    Variables that are package scope are reloaded each time a new package is loaded
    Variables that are module scope are reloaded each time a new module is loaded
    Variables that are function scope are reloaded each time a new function is loaded

    When creating an environment an optional file may be given that will load a repo scope environment
    from the file.  This is useful for setting up the environment for a run.  An environment as
    a dictionary may also be provided.

    The semantics of the environment work like pytest. Each environment function is yielded
    one at a time when the module is loaded and yielded again when unloaded (in reverse order),
    if the environment function is a generator.  If the environment function is not a generator
    it is called once when the module is loaded.

    The yield method would be used for something like a database connection that needs to be
    established and torn down, while the non-generator would be used for something like a
    configuration file that is read once and used for the duration of the run.

    Note that care should be taken when using mutable data structures that aren't reloaded.  Ideally
    frozen data structures should be used to avoid nasty side effects.

    """

    def __init__(self,env=None):
        self.environment = {}
        if env:
            for k,v in env.items():
                self.add(k,v)

    def __call__(self, name):
        if name not in self.environment:
            raise SplintException(f"The name {name} is not in the environment.")
        return self.environment[name]

    def add(self, name, value):
        if name in self.environment:
            raise SplintException(f"The name {name} is already in the environment.")
        self.environment[name] = value

