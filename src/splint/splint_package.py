import logging
import pathlib
import sys
from typing import List

from .splint_environment import SplintEnvironment
from .splint_exception import SplintException
from .splint_filter import filter_none
from .splint_module import SplintModule


class SplintPackage:
    def __init__(
        self,
        folder="check",
        module_glob="check_*.py",
        function_prefix="check_",
        auto_load=True,
        name=None,
        env: SplintEnvironment = None,
    ):
        self.modules: List[SplintModule] = []
        self.folder: pathlib.Path = pathlib.Path(folder)
        self.module_glob: str = module_glob
        self.function_prefix: str = function_prefix
        self.env: SplintEnvironment = env or {}
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

        if auto_load:
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
        if not any(
            pathlib.Path(path).resolve() == absolute_folder_path for path in sys.path
        ):
            # If it's not, add it to sys.path
            sys.path.insert(0, str(absolute_folder_path))

    @property
    def module_count(self) -> int:
        return 0 if not self.modules else len(self.modules)

    def load_modules(self, glob=None)->List[SplintModule]:
        checkfile_glob = glob or self.module_glob

        for file_path in sorted(self.folder.glob(checkfile_glob)):
            module_name = f"{file_path.stem}"

            module = SplintModule(module_name, module_file=file_path, auto_load=True)
            self.modules.append(module)

        return self.modules

    def get(self, module_name)->SplintModule:
        for module in self.modules:
            if module.module_name == module_name:
                return module
        return None

    def ruids(self):
        """get a list of all the RUIDS in a package"""
        ruids = []
        for module in self.modules:
            ruids.extend(module.ruids())
        return sorted(ruids)