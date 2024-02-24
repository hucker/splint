"""
SplintModule is a class that represents a module that contains a set of functions that can be run. A module
typically represents a file that is imported into the system by finding all function that
start with a certain prefix and adding them to the list of functions to be managed by splint.
"""

import importlib
import pathlib
import sys
from collections import Counter
from typing import List

from .splint_exception import SplintException
from .splint_function import SplintFunction


class SplintModule:
    def __init__(self, module_name, module_file, function_prefix=None, auto_load=True):
        self.module_name = module_name
        self.functions: List[SplintFunction] = []
        self.module = None
        self.module_file = module_file
        self.function_prefix = function_prefix or "check_"
        self.doc = ""
        if auto_load:
            self.load()

    def __str__(self):
        return f"SplintModule({self.module_name=},{self.function_count=} functions)"

    @property
    def function_count(self) -> int:
        return 0 if not self.functions else len(self.functions)

    def add_function(self, module, function):
        function = SplintFunction(function, module)
        self.functions.append(function)

    def _add_sys_path(self, module_file):

        """Add a module's directory to sys.path if it's not already there."""

        # Construct a Path object from the provided file path and get its parent directory
        module_dir = pathlib.Path(module_file).parent.resolve()

        # Check if the module directory is already in sys.path
        if module_dir not in (pathlib.Path(path).resolve() for path in sys.path):
            sys.path.insert(0, str(module_dir))

    # If not, add it to sys.path

    def load(self, module_name=None):
        module_name = module_name or self.module_name
        self._add_sys_path(self.module_file)
        try:
            module = importlib.import_module(module_name)
            self.module = module
            self.doc = module.__doc__
            self.load_functions(module)
            return True

        except ImportError as e:
            raise SplintException(f"Can't load {module_name}: {e}")

    def load_functions(self, module):
        """Look through all the functions in the module and if they start with the function_prefix
        add them to the list of functions."""

        module = module or self.module

        for name in dir(module):
            if name.startswith("_"):
                continue
            obj = getattr(module, name)
            if not callable(obj):
                continue
            if not name.startswith(self.function_prefix):
                continue
            self.add_function(module, obj)

        duplicate_ruids = [item for item, count in Counter(self.ruids()).items() if count > 1 and item != '']

        if duplicate_ruids:
            raise SplintException(f"Duplicate RUIDs found in module: {','.join(duplicate_ruids)}")

    def ruids(self):
        """
        Return a list of all the RUIDs in the module.
        Note that this can have duplicates.  The list is
        sorted to facilitate comparison.

        RUID = rule identifier
        """
        return sorted(function.ruid for function in self.functions)
