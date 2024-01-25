import importlib
from typing import List
from .splint_function import SplintFunction
import logging
import sys
from .splint_exception import SplintException
from .splint_filter import filter_none


class SplintModule:
    def __init__(self, module_name, module_file, function_prefix=None, autoload=True):
        self.module_name = module_name
        self.functions: List[SplintFunction] = []
        self.module = None
        self.module_file = module_file
        self.function_prefix = function_prefix or "check_"
        self.doc = ""
        if autoload:
            self.load()

    def __str__(self):
        return f"SplintModule({self.module_name=},{self.function_count=} functions)"

    @property
    def function_count(self) -> int:
        return 0 if not self.functions else len(self.functions)

    def add_function(self, module, function):
        function = SplintFunction(module, function)
        self.functions.append(function)

    def load(self, module_name=None):
        module_name = module_name or self.module_name
        try:
            module = importlib.import_module(module_name)
            self.module = module
            self.doc = module.__doc__
            self.load_functions(module)
            logging.info(f"Loaded module {self}")
            return True

        except ImportError as e:
            raise SplintException(f"Can't load {module_name}: {e}")

    def load_functions(self, module):
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

    def yield_all(self, filter_func=filter_none()):
        for function in self.functions:
            if not function.skip and filter_func(function):
                for result in function():
                    yield result

    def run_all(self, filter_func=filter_none()):
        results = list(self.yield_all(filter_func=filter_func))
        return results
