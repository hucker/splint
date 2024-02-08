import random
from typing import List

from .splint_exception import SplintException
from .splint_function import SplintFunction
from .splint_module import SplintModule
from .splint_package import SplintPackage
from .splint_ruid import valid_ruids, ruid_issues, empty_ruids

def random_order():
    """Return a random number to order the functions."""
    return lambda _: random.random()

def order_by_pkg_mod_func(s_func: SplintFunction):
    """Return a string to order the functions by package, module and function."""
    return f"{s_func.pkg_name}.{s_func.module_name}.{s_func.func_name}"




def exclude_ruids(ruids: List[str]):
    """Return a filter function that will exclude the ruids from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.ruid not in ruids

    return filter_func


def exclude_tags(tags: List[str]):
    """Return a filter function that will exclude the tags from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.tag not in tags

    return filter_func


def exclude_levels(levels: List[int]):
    """Return a filter function that will exclude the levels from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.level not in levels

    return filter_func


def exclude_phases(phases: List[str]):
    """Return a filter function that will exclude the phases from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.phase not in phases

    return filter_func


def keep_ruids(ruids: List[str]):
    """Return a filter function that will keep the ruids from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.ruid in ruids

    return filter_func


def keep_tags(tags: List[str]):
    """Return a filter function that will keep the tags from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.tag in tags

    return filter_func


def keep_levels(levels: List[int]):
    """Return a filter function that will keep the levels from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.level in levels

    return filter_func


def keep_phases(phases: List[str]):
    """Return a filter function that will keep the phases from the list."""

    def filter_func(splint_function: SplintFunction):
        return splint_function.phase in phases

    return filter_func


class SplintChecker:

    def __init__(
        self,
        packages: List[SplintPackage] | None = None,
        modules: List[SplintModule] | None = None,
        functions: List[SplintFunction] | None = None,
        env=None,
    ):
        """
        User can provide a list of packages, modules and functions to check.

        If rule functions take parameters then the user can provide an environment to be used
        for the rule functions

        """

        if isinstance(packages, list) and len(packages) > 1:
            self.packages = packages
            if not all(isinstance(p, SplintPackage) for p in packages):
                raise SplintException(
                    "Packages must be a list of SplintPackage objects."
                )
        elif isinstance(packages, SplintPackage):
            self.packages = [packages]
        elif not packages:
            self.packages = []
        else:
            raise SplintException("Packages must be a list of SplintPackage objects.")

        if isinstance(modules, list) and len(modules) > 1:
            self.modules = modules
            for m in modules:
                if not isinstance(m, SplintModule):
                    raise SplintException(
                        "Modules must be a list of SplintModule objects."
                    )
        elif isinstance(modules, SplintModule):
            self.modules = [modules]
        elif not modules:
            self.modules = []
        else:
            raise SplintException("Modules must be a list of SplintModule objects.")

        if isinstance(functions, list) and len(functions) > 1:
            self.functions = functions
            for f in functions:
                if not isinstance(f, SplintFunction):
                    raise SplintException(
                        "Functions must be a list of SplintFunction objects."
                    )
        elif not functions:
            self.functions = []
        else:
            raise SplintException("Functions must be a list of SplintFunction objects.")

        if env:
            self.env = env
        else:
            self.env = {}

        self.collected = []
        self.pre_collected = []

        if not self.packages and not self.modules and not self.functions:
            raise SplintException(
                "You must provide at least one package, module or function to check."
            )

    def pre_collect(self)->List[SplintFunction]:
        """
        Collect all the functions from the packages, modules and functions with no filtering.
        This list of functions is will be filtered by the checker before running checks.

        Returns:
            _type_: _description_
        """

        self.pre_collected = []

        for pkg in self.packages:
            for module in pkg.modules:
                for function in module.functions:
                    self.pre_collected.append(function)

        for module in self.modules:
            for function in module.functions:
                self.pre_collected.append(function)

        for function in self.functions:
            self.pre_collected.append(function)

        # List of all possible functions that could be run
        return self.pre_collected

    def prepare(self, filter_functions=None, order_function=None):
        """
        Prepare the collected functions for running checks.

        Run through the collected functions to prepart the checks that will be run.
        A list of filter functions may be provided to filter the functions. Filter
        functions must return True if the function should be kept.

        An order function may be provided to sort the function sbefore running them

        Args:
            filter_functions (_type_, optional): _description_. Defaults to None.
            order_function (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        # If no filter functions are provided then use a default one allows all functions
        filter_functions = filter_functions or [lambda _: True]

        # At this point we have all the functions in the packages, modules and functions
        # Now we need to filter out the ones that are not wanted. Filter functions return
        # True if the function should be kept
        self.collected = []
        for splint_func in self.pre_collected:
            if all(f(splint_func) for f in filter_functions):
                self.collected.append(splint_func)

        # If an order function is provided then sort the collected functions,
        # you could sort by tag, level, ruid etc.  Not sure this will ever be
        # used but it's here.
        if order_function:
            self.collected = sorted(self.collected, key=order_function)

        # The collected list has the functions that will be run to verify operation
        # of the system.

        # If the user has provided valid ruids for all functions (or for none) then
        # we can proceed.  If not then we need to raise an exception and show the issues.
        ruids = [f.ruid for f in self.collected]

        if empty_ruids(ruids) or valid_ruids(ruids):
            return self.collected
        else:
            raise SplintException(f"There are duplicate or missing RUIDS: {ruid_issues(ruids)}")

        # List of functions that will be run
        return self.collected


    def ruids(self):
        """
        Return a list of all of the RUIDs in the collected functions.

        Returns:
            _type_: _description_
        """
        ruids = [f.ruid for f in self.collected]

        return sorted(set(f.ruid for f in self.collected))

    def yield_all(self, env=None):
        """
        Yield all the results from the collected functions

        Args:
            env: The environment to use for the rule functions

        Yields:
            _type_: SplintResult
        """



        # Note that it is possible for the collected list to be
        # empty.  This is not an error condition.  It is possible
        # that the filter functions have filtered out all of the
        # functions.
        # Oddly enough this simple loop runs the whole program.
        for function in self.collected:
            function.env = env
            for result in function():
                yield result

    def run_all(self, env=None):
        """
        List version of yield all.
        """
        return list(self.yield_all(env=env))
