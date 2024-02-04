
import pathlib
import sys
import logging
from .splint_exception import SplintException
from .splint_module import SplintModule
from .splint_environment import SplintEnvironment
from .splint_filter import filter_none
from typing import List

class SplintPackage:
    def __init__(
        self,
        folder="check",
        module_glob="check_*.py",
        function_prefix="check_",
        autoload=True,
        name=None,
        env: SplintEnvironment = None,
    ):
        self.modules: List[SplintModule] = []
        self.folder:pathlib.Path = pathlib.Path(folder)
        self.module_glob:str = module_glob
        self.function_prefix:str = function_prefix
        self.env:SplintEnvironment = env or {}
        self.results = []

        if not name:
            self.name = self.folder.name
        else:
            self.name = name

        self.folder = self.folder.resolve()

        # Add to module search path

        self._add_folder_to_sys_path(self.folder)

        self._verify_dir()

        if self.env is None:
            raise SplintException("An environment has not been defined.")

        if autoload:
            self.load_modules()

    def _verify_dir(self):
        # Catastrophic, splint can't work with in check folder
        if not self.folder.exists():
            raise SplintException(
                f"The splint check folder '{self.folder}' does not exist."
            )

    @staticmethod
    def _add_folder_to_sys_path(folder):
        if not folder:
            return

        # Convert the folder path to an absolute path
        absolute_folder_path = pathlib.Path(folder).resolve()

        # Check if the absolute folder path is in sys.path
        if not any(pathlib.Path(path).resolve() == absolute_folder_path for path in sys.path):
            # If it's not, add it to sys.path
            sys.path.insert(0, str(absolute_folder_path))


    @property
    def module_count(self) -> int:
        return 0 if not self.modules else len(self.modules)

    def load_modules(self, glob=None):
        checkfile_glob = glob or self.module_glob

        logging.info(
            f"Loading splint modules from %s with pattern {checkfile_glob}", self.folder
        )

        for file_path in sorted(self.folder.glob(checkfile_glob)):
            module_name = f"{file_path.stem}"

            module = SplintModule(module_name, module_file=file_path, autoload=True)
            self.modules.append(module)

        return self.modules


    def get(self, module_name):
        for module in self.modules:
            if module.module_name == module_name:
                return module
        return None

    def suids(self):
        """get a list of all the SUIDS in a package"""
        suids = []
        for module in self.modules:
            suids.extend(module.suids())
        return sorted(suids)

    def yield_all(self,filter_func=filter_none()):
        """
        Generator method to run all functions in the modules that satisfy the filter_func condition.

        This method iterates over all modules and their functions. If a function satisfies the condition
        specified by filter_func, it is run and its results are yielded one by one.

        Args:
            filter_func (callable): A function that takes a SplintFunction instance as an argument and
                                    returns a boolean. Only functions for which this returns True are run.
                                    By default, all functions are run.

        Yields:
            SplintResult: The result of each function that satisfies the filter_func condition.
        """
        for module in self.modules:
            results = module.yield_all(filter_func=filter_func)
            for result in results:
                yield result


    def run_all(self,filter_func=filter_none()):
        return list(self.yield_all(filter_func=filter_func))