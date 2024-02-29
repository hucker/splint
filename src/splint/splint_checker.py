import datetime as dt
from typing import List

import splint
from .splint_exception import SplintException
from .splint_function import SplintFunction
from .splint_module import SplintModule
from .splint_package import SplintPackage
from .splint_result import SplintResult
from .splint_ruid import empty_ruids, ruid_issues, valid_ruids
from .splint_score import ScoreByResult, ScoreStrategy


def exclude_ruids(ruids: List[str]):
    """Return a filter function that will exclude the ruids from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.ruid not in ruids

    return filter_func


def exclude_tags(tags: List[str]):
    """Return a filter function that will exclude the tags from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.tag not in tags

    return filter_func


def exclude_levels(levels: List[int]):
    """Return a filter function that will exclude the levels from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.level not in levels

    return filter_func


def exclude_phases(phases: List[str]):
    """Return a filter function that will exclude the phases from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.phase not in phases

    return filter_func


def keep_ruids(ruids: List[str]):
    """Return a filter function that will keep the ruids from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.ruid in ruids

    return filter_func


def keep_tags(tags: List[str]):
    """Return a filter function that will keep the tags from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.tag in tags

    return filter_func


def keep_levels(levels: List[int]):
    """Return a filter function that will keep the levels from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.level in levels

    return filter_func


def keep_phases(phases: List[str]):
    """Return a filter function that will keep the phases from the list."""

    def filter_func(s_func: SplintFunction):
        return s_func.phase in phases

    return filter_func


def debug_progress(count, msg=None, result: SplintResult = None
):  # pylint: disable=unused-argument
    """Print a debug message."""
    if msg:
        print(msg)
    if result:
        print("+" if result.status else "-", end="")


def quiet_progress(step=0,msg=None, result=None):  # pylint: disable=unused-argument
    """
    Updates and prints the progress in a quiet mode...as in does nothing in this case.

    A real progress bar will use the step number to determine the progress compared
    to the total number of split functions (not results).  A message is provided for
    easy progress bars, while the last result is provided to allow streaming info.

    Args:
        steps (int): Total number of steps for the progress.
        msg: Informational message for the current step in the process

    Returns:
        None

    Example:
        quiet_progress(10, 0.5)

    This will do nothing since this function just shows the signature.
    """
    # Your function's code here
    pass


def orderby_tag():
    """Order collected list by tag"""

    def sort_key(x: SplintFunction):
        return x.tag

    return sort_key


def orderby_ruid():
    """Order collected list by tag"""

    def sort_key(x: SplintFunction):
        return x.ruid

    return sort_key


class SplintChecker:
    """
    Collect all the rule functions and order them if need be and then run them.

    Calling yield_all or run_all will iterate over the rules and return all the results.
    """

    def __init__(
            self,
            packages: List[SplintPackage] | None = None,
            modules: List[SplintModule] | None = None,
            check_functions: List[SplintFunction] | None = None,
            progress_callback=None,
            score_strategy: ScoreStrategy | None = None,
            env=None,
            abort_on_fail=False,
            abort_on_exception=False,
            auto_setup: bool = False,
    ):
        """
        User can provide a list of packages, modules and functions to check.

        If rule functions take parameters then the user can provide an environment to be used
        for the rule functions

        """

        if isinstance(packages, list) and len(packages) >= 1:
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

        if isinstance(modules, list) and len(modules) >= 1:
            self.modules: List[SplintModule] = modules
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

        if isinstance(check_functions, list) and len(check_functions) >= 1:
            self.check_functions: List[SplintFunction] = check_functions
            f:SplintFunction = None
            for f in check_functions:
                if not isinstance(f, SplintFunction):
                    raise SplintException(
                        "Functions must be a list of SplintFunction objects."
                    )
                # Since we are building up a module from nothing we give it a generic name
                f.module = "adhoc"
        elif not check_functions:
            self.check_functions: List[SplintFunction] = []
        else:
            raise SplintException("Functions must be a list of SplintFunction objects.")

        # If the user has not provided a score strategy then use the simple one
        self.score_strategy = score_strategy or ScoreByResult()
        self.score = 0.0

        if env:
            self.env = env
        else:
            self.env = {}

        # Install a default if needed (should this be a list?)
        self.progress_callback = progress_callback or quiet_progress

        # If any fail result occurs stop processing.
        self.abort_on_fail = abort_on_fail

        # If any exception occurs stop processing
        self.abort_on_exception = abort_on_exception

        self.collected = []
        self.pre_collected = []
        self.start_time = dt.datetime.now()
        self.end_time = dt.datetime.now()
        self.results:List[splint.SplintResult] = []

        if not self.packages and not self.modules and not self.check_functions:
            raise SplintException(
                "You must provide at least one package, module or function to check."
            )

        # For some use cases there is no need for special setup so just do auto setup
        # to clean up the startup.  Real code will likely need to be sophisticated
        # with prepare...
        if auto_setup:
            self.pre_collect()
            self.prepare()

    def pre_collect(self) -> List[SplintFunction]:
        """
        Collect all the functions from the packages, modules and functions with no filtering.
        This list of functions is will be filtered by the checker before running checks.

        Returns:
            _type_: _description_
        """

        self.pre_collected = []

        for pkg in self.packages:
            for module in pkg.modules:
                for function in module.check_functions:
                    self.pre_collected.append(function)

        for module in self.modules:
            for function in module.check_functions:
                self.pre_collected.append(function)

        for function in self.check_functions:
            self.pre_collected.append(function)

        # List of all possible functions that could be run
        return self.pre_collected

    def prepare(self, filter_functions=None, order_function=None):
        """
        Prepare the collected functions for running checks.

        Run through the collected functions to prepare the checks that will be run.
        A list of filter functions may be provided to filter the functions. Filter
        functions must return True if the function should be kept.

        An order function may be provided to sort the functions before running them

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
        # you could sort by tag, level, ruid etc.  Not sure if this will ever be
        # used, but it's here.
        if order_function:
            self.collected = sorted(self.collected, key=order_function)

        # The collected list has the functions that will be run to verify operation
        # of the system.

        # If the user has provided valid ruids for all functions (or for none) then
        # we can proceed.  If not then we need to raise an exception and show the issues.
        ruids = [f.ruid for f in self.collected]

        # If the user decided to set up ruids for every function OR if they didn't configure
        # any ruids then we can just run with the collected functions.
        if empty_ruids(ruids) or valid_ruids(ruids):
            return self.collected

        # Otherwise there is a problem.
        raise SplintException(
            f"There are duplicate or missing RUIDS: {ruid_issues(ruids)}"
        )


    def load_environments(self):

        # Prime the environment with top level config
        # This should be json-able things
        full_env = self.env.copy()

        for m in self.modules:
            for env_func in m.env_functions:
                # TODO: There should be exceptions on collisions
                full_env.update(env_func(full_env))
        return full_env

    @property
    def ruids(self):
        """
        Return a list of all the RUIDs in the collected functions.

        Returns:
            _type_: _description_
        """
        r = sorted(set(f.ruid for f in self.collected))
        return r

    @property
    def levels(self):
        """
        Return a list of all the levls in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.level for f in self.collected))

    @property
    def tags(self):
        """
        Return a list of all the tags in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.tag for f in self.collected))

    @property
    def phases(self):
        """
        Return a list of all the phases in the collected functions.

        Returns:
            _type_: _description_
        """
        return sorted(set(f.phase for f in self.collected))

    def yield_all(self, env=None):
        """
        Yield all the results from the collected functions

        Args:
            env: The environment to use for the rule functions

        Yields:
            _type_: SplintResult
        """

        class AbortYieldException(Exception):
            """Allow breaking out of multi level loop without state variables"""
            pass

        # Note that it is possible for the collected list to be
        # empty.  This is not an error condition.  It is possible
        # that the filter functions have filtered out all the
        # functions.
        count = 0
        self.progress_callback(count,"Start Rule Check")
        self.start_time = dt.datetime.now()

        try:

            env = self.load_environments()

            result: splint.SplintResult=None

            # Count here to enable progress bars
            for count,function in enumerate(self.collected,start=1):

                # Lots of magic here
                function.env = env

                self.progress_callback(count,f"Func Start {function.function_name}")
                for result in function():
                    yield result

                    # Check early exits
                    if self.abort_on_fail and result.status is False:
                        raise AbortYieldException()

                    if self.abort_on_exception and result.except_:
                        raise AbortYieldException()

                    # Stop yielding from a function
                    if function.finish_on_fail and result.status == False:
                        self.progress_callback(count,f"Early exit. {function.function_name} failed.")
                        break
                    self.progress_callback(count,"", result)
                self.progress_callback(count,"Func done.")

        except AbortYieldException:
            if self.abort_on_fail:
                self.progress_callback(count,f"Abort on fail: {function.function_name}")
            if self.abort_on_exception:
                self.progress_callback(count,f"Abort on exception: {function.function_name}")

        self.end_time = dt.datetime.now()
        self.progress_callback(count,"Rule Check Complete.")

    def run_all(self, env=None):
        """
        List version of yield all.

        """
        self.results = list(self.yield_all(env=env))
        self.score = self.score_strategy(self.results)
        self.progress_callback(self.function_count,f"Score = {self.score:.1f}")
        return self.results

    @property
    def clean_run(self):
        """ No exceptions """
        return all(not r.except_ for r in self.results)

    @property
    def perfect_run(self):
        """No fails or skips"""
        return all(r.status and not r.skipped for r in self.results)

    @property
    def skip_count(self):
        """Number of skips"""
        return len([r for r in self.results if r.skipped])

    @property
    def pass_count(self):
        """Number of passes"""
        return len([r for r in self.results if r.status and not r.skipped])

    @property
    def fail_count(self):
        """Number of fails"""
        return len([r for r in self.results if not r.status and not r.skipped])

    @property
    def total_count(self):
        return len(self.results)

    @property
    def function_count(self):
        return len(self.collected)

    @property
    def module_count(self):
        cnt = len(self.modules)
        for pkg in self.packages:
            for m in pkg.modules:
                cnt += 1

        return cnt

    @property
    def module_names(self):
        names = []
        for module in self.modules:
            names.append(module.name)
        for pkg in self.packages:
            for m in pkg.modules:
                names.append(m.module_name)
        return names


    @property
    def package_count(self):
        return len(self.packages)

    def get_header(self) -> dict:
        header = {
            "package_count": self.package_count,
            "module_count": self.module_count,
            "modules": self.module_names,
            "function_count": self.function_count,
            "tags": sorted(list(set(f.tag for f in self.collected))),
            "levels": sorted(list(set(f.level for f in self.collected))),
            "phases": sorted(list(set(f.phase for f in self.collected))),
            "ruids": self.ruids,
            "score": self.score,
        }
        return header

    def as_dict(self):
        """
        Return a dictionary of the results.
        """
        h = self.get_header()

        r = {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": (self.end_time - self.start_time).total_seconds(),

            "functions": [f.function_name for f in self.check_functions],
            "passed_count": self.pass_count,
            "failed_count": self.fail_count,
            "skip_count": self.skip_count,
            "total_count": self.total_count,

            # the meat of the output livers here
            "results": [r.as_dict() for r in self.results],
        }
        return h | r
