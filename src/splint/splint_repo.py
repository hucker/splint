
from .splint_package import SplintPackage
from  .splint_exception import SplintException
from .splint_result import SplintResult
from typing import List
import pathlib


class SplintRepo:
    def __init__(self, pkg_folder=None, pkg_glob="pkg_*", auto_load=True, stop_on_exc=False):
        self.packages: List[SplintPackage] = []
        self.pkg_folders = list(pathlib.Path(pkg_folder).glob(pkg_glob))
        self.pkg_glob = pkg_glob
        self.stop_on_exc = stop_on_exc
        if auto_load and self.pkg_folders:
            self.load_packages()

    def load_packages(self, pkg_folders=None):
        self.packages = []
        for folder in pkg_folders or self.pkg_folders:
            try:
                self.packages.append(SplintPackage(folder=str(folder)))
            except SplintException as se:
                return False
        return True

    def yield_all(self):
          """TODO: This needs to be updated to yield results from all packages."""
          pass

    def run_pkgs(self):
        pkg: SplintPackage = None
        results = []
        for pkg in self.packages:
            try:
                results.extend(pkg.run_all())
            except SplintException as se:
                results.append(SplintResult(status=False, msg=f"Exception caught Splint Repo.run_all package={pkg.folder} {se}", except_=se,tag='__splint__'))
                if self.stop_on_exc:
                    break

        return results
