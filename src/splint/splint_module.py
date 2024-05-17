"""
SplintModule represents a module with a functions set that can be run. A module
typically symbolizes a file imported into the system. It does this by identifying
all functions starting with a certain prefix and adding them to a list managed
by splint.
"""

import importlib
import inspect
import pathlib
import sys
from collections import Counter
from typing import List

from .splint_exception import SplintException
from .splint_function import SplintFunction


class SplintModule:
    """
    A module is a collection of functions that is read from a file.  The check_ functions
    are used to verify rules, while the env_functions are used to set up any parameters
    that the rule functions might need.
    """

    def __init__(
            self,
            module_name,
            module_file,
            check_prefix="check_",
            env_prefix="env_",
            env_functions=None,
            auto_load=True,
    ):
        self.module_name = module_name
        self.check_functions: List[SplintFunction] = []
        self.env_functions: List = env_functions or []
        self.module = None
        self.module_file = module_file
        self.check_prefix = check_prefix
        self.env_prefix = env_prefix
        self.doc = ""
        if auto_load:
            self.load()

    def __str__(self):
        return (
            f"SplintModule({self.module_name=},{self.check_function_count=} functions)"
        )

    @property
    def check_function_count(self) -> int:
        """Return the check function count..."""
        return len(self.check_functions) if self.check_functions else 0

    def add_check_function(self, module, function):
        """Wrap the function in a splint function"""
        function = SplintFunction(function, module)
        self.check_functions.append(function)

    def add_env_function(self, func):
        """Add a discovered environment function to the list"""
        self.env_functions.append(func)

    @staticmethod
    def _add_sys_path(module_file):
        """Add a module's directory to sys.path if it's not already there."""

        # Construct a Path object from the provided file path and get its parent directory
        module_dir = pathlib.Path(module_file).parent.resolve()

        # Check if the module directory is already in sys.path
        if module_dir not in (pathlib.Path(path).resolve() for path in sys.path):
            sys.path.insert(0, str(module_dir))

        return sys.path

    # If not, add it to sys.path

    def load(self, module_name=None):
        """Load a module using importlib."""
        module_name = module_name or self.module_name
        self._add_sys_path(self.module_file)
        try:
            module = importlib.import_module(module_name)
            self.module = module
            # self.doc = module.__doc__
            self.doc = inspect.getdoc(module)
            self.load_special_functions(module)
            return True

        except ImportError as iex:
            raise SplintException(f"Can't load {module_name}:{iex.msg}") from iex

    def load_special_functions(self, module):
        """Look through all the functions in the module and load the check/env functions"""

        module = module or self.module

        # Dir givens you every element in the module object and allows us to look
        # for check functions that look a certain way
        check_func_count = 0
        for name in dir(module):
            if name.startswith("_"):
                continue
            obj = getattr(module, name)

            if not callable(obj):
                continue

            # Load environment functions
            if name.startswith(self.env_prefix):
                self.add_env_function(obj)

            # Load check functions.  We number them because we care about the 'file' order
            # The file order will let us sort/resort functions and access file order if we want it.
            if name.startswith(self.check_prefix):
                check_func_count += 1
                obj.index = check_func_count
                self.add_check_function(module, obj)

        # Strictly speaking this doesn't need to happen here, it could be checked later
        duplicate_ruids = [
            item
            for item, count in Counter(self.ruids()).items()
            if count > 1 and item != ""
        ]

        if duplicate_ruids:
            raise SplintException(
                f"Duplicate RUIDs found in module: {','.join(duplicate_ruids)}"
            )

    def ruids(self):
        """
        Return a list of all the RUIDs in the module.
        Note that this can have duplicates.  The list is
        sorted to facilitate comparison.

        RUID = rule identifier
        """
        return sorted(function.ruid for function in self.check_functions)
