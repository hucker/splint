"""
This class manages running the checker against a list of functions.
There is also support for low level progress for functions/classes.
"""
import datetime as dt
from abc import ABC, abstractmethod
from typing import Any, List

import pandas as pd

from .splint_exception import SplintException
from .splint_function import SplintFunction
from .splint_immutable import SplintEnvDataFrame, SplintEnvDict, SplintEnvList, SplintEnvSet
from .splint_module import SplintModule
from .splint_package import SplintPackage
from .splint_rc import SplintRC
from .splint_result import SplintResult
from .splint_ruid import empty_ruids, ruid_issues, valid_ruids
from .splint_score import ScoreByResult, ScoreStrategy


# pylint: disable=R0903
class SplintProgress(ABC):
    """ Base class for all splint progress bars"""

    def __init__(self):
        pass

    @abstractmethod
    def __call__(self,
                 current_iteration: int,
                 max_iterations,
                 text: str,
                 result=None):  # pragma: no cover
        pass


# pylint: disable=R0903
class SplintNoProgress(SplintProgress):
    """Progress 'bar' that does nothing.  Useful for testing and debugging."""

    def __call__(self, current_iteration: int,
                 max_iterations,
                 text: str, result=None):
        """Don't do anything for progress.  This is useful for testing."""


# pylint: disable=R0903
class SplintDebugProgress(SplintProgress):
    """ Progress 'bar' that is useful for debugging by printing data to the console"""

    def __call__(self, current_iteration: int, max_iteration: int, msg: str,
                 result=None):  # pylint: disable=unused-argument
        """Print a debug message."""
        if msg:
            print(msg)
        if result:
            print("+" if result.status else "-", end="")


def _param_str_list(params: List[str] | str | None,
                    disallowed=' ,!@#$%^&*(){}[]<>~`-+=\t\n\'"') -> List[str]:
    """
    Allow user to specify "foo fum" instead of ["foo","fum"] or slightly more
    shady "foo" instead of ["foo"].  This is strictly for reducing friction
    for the programmer.

    Also note: the disallowed characters is just me being courteous and trying to protect
               you from yourself.  If there are other dumb characters that
               I missed please submit a PR as I have no intention of walling off
               everything in a dynamic language.

    Returns: List of Strings

    Args:
        params: "foo fum" or ["foo","fum"]


    """

    # Null case...on could argue they meant the empty string as a name
    if params is None or params == [] or isinstance(params, str) and params.strip() == '':
        return []

    if isinstance(params, str):
        params = params.split()

    for param in params:
        if not isinstance(param, str):
            raise SplintException(f"Invalid parameter list {param}")
        bad_chars = [c for c in disallowed if c in param]
        if bad_chars:
            raise SplintException(f"Parameter '{bad_chars}' has a space in it.  ")

    return params


def _param_int_list(params: List[str] | List[int] | int | str) -> List[int]:
    """
    Allow user to specify "1 2 3" instead of [1,2,3] or slightly more
    shady 1 instead of [1].  For small numbers this is a wash but for
    symmetry with str_list it included it.

    NOTE: The separator is the default for split...whitespace

    Args:
        params: "1 2" or [1,2]

    Returns: List of Integers

    """

    if (isinstance(params, str) and params.strip() == '') or not params:
        return []
    if isinstance(params,list):
        return [int(v) for v in params]
    if isinstance(params, int):
        return [int(params)]
    if isinstance(params, str):
        str_params = params.split()
        try:
            return [int(str_param) for str_param in str_params]
        except ValueError as vex:
            raise SplintException(f"Invalid integer parameter in {params}") from vex

    raise SplintException(f"Invalid integer parameter list: {params}")


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


def debug_progress(count, msg: str | None = None, result: SplintResult | None = None
                   ):  # pylint: disable=unused-argument
    """Print a debug message."""
    if msg:
        print(msg)
    if result:
        print("+" if result.status else "-", end="")


class SplintChecker:
    """
    A checker object is what manages running rules against a system.

    THe life cycle of a checker object is

    1) Load what ever packages/modules/functions are associated with a system as
       a collection of functions that could be run.
    2) Load any environment that may be needed for the rules.
    2) Optionally filter those functions based on any of the function attributes.
    3) Check all the rules and collect the results while providing status using
       a user specified progress object.
    4) Score the results based on the scoring strategy.
    5) Return the result object as object data or json data.
    """

    def __init__(
            self,
            packages: List[SplintPackage] | None = None,
            modules: List[SplintModule] | None = None,
            check_functions: List[SplintFunction] | None = None,
            progress_object: SplintProgress | None = None,
            score_strategy: ScoreStrategy | None = None,
            rc: SplintRC | None = None,
            env: dict[str, Any] | None = None,
            abort_on_fail=False,
            abort_on_exception=False,
            auto_setup: bool = False,
            auto_ruid: bool = False,
    ):
        """

        
        Args:
            packages: List of SplintPackage objs to check. 
                      If not provided, default = [] .
            modules: A list of SplintModule objs to check. 
                     If not provided, default = [].
            check_functions: A list of SplintFunction objs to check. If not provided, default = [].
            progress_object: A SplintProgress objs for tracking progress. 
                             If not provided, def = SplintNoProgress.
            score_strategy: A ScoreStrategy objs for scoring the results. 
                            If not provided, def = ScoreByResult.
            env: A dict containing additional env variables. 
                            If not provided, def = {}
            abort_on_fail: A bool flag indicating whether to abort a fail result occurs. def =False.
            abort_on_exception: A bool flag indicating whether to abort on exceptions. def=False.
            auto_setup: A bool flag automatically invoke pre_collect/prepare. def=False.
            auto_ruid: A bool flag automatically generate rule_ids if they don't exist.
        Raises:
            SplintException: If the provided packages, modules, or check_functions 
                             are not in the correct format.

        """

        self.packages = self._process_packages(packages)
        self.modules = self._process_modules(modules)
        self.check_functions = self._process_check_funcs(check_functions)

        # If the user has not provided a score strategy then use the simple one
        self.score_strategy = score_strategy or ScoreByResult()
        self.score = 0.0

        # Allow an RC object to be specified.
        self.rc = rc

        # If we are provided with an environment we save it off but first wrap it in
        # a class that guards reasonably against writes to the underlying environment
        # data.
        if env:
            self.env = self._make_immutable_env(env)
        else:
            self.env = {}
        
        # THis dict has the environment values that are NULL
        self.env_nulls:dict[str,Any] = {}

        # Connect the progress output to the checker object.  The NoProgress
        # class is a dummy class that does no progress reporting.
        self.progress_callback: SplintProgress = progress_object or SplintNoProgress()

        # If any fail result occurs stop processing.
        self.abort_on_fail = abort_on_fail

        # If any exception occurs stop processing
        self.abort_on_exception = abort_on_exception

        # These two have the collection of all checker functions from packages, modules, and adhoc
        self.collected: List[SplintFunction] = []
        self.pre_collected: List[SplintFunction] = []

        self.start_time = dt.datetime.now()
        self.end_time = dt.datetime.now()
        self.results: List[SplintResult] = []
        self.auto_ruid = auto_ruid

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

    @staticmethod
    def _make_immutable_env(env: dict) -> dict:
        """
        Converts mutable containers in a dictionary to immutable versions.
        """
        for key, value in env.items():

            # Detect mutable objects and convert them to immutable ones
            if isinstance(value, list):
                env[key] = SplintEnvList(value)
            elif isinstance(value, dict):
                env[key] = SplintEnvDict(value)
            elif isinstance(value, pd.DataFrame):
                env[key] = SplintEnvDataFrame(value)
            elif isinstance(value, set):
                env[key] = SplintEnvSet(value)

        return env

    @staticmethod
    def _process_packages(packages: List[SplintPackage] | None) -> List[SplintPackage]:
        """ Allow packages to be in various forms"""
        if not packages:
            return []
        if isinstance(packages, SplintPackage):
            return [packages]
        if isinstance(packages, list) and all(isinstance(p, SplintPackage) for p in packages):
            return packages
        raise SplintException('Packages must be a list of SplintPackage objects.')

    @staticmethod
    def _process_modules(modules: List[SplintModule] | None) -> List[SplintModule]:
        """ Allow modules to be in various forms"""
        if not modules:
            return []
        if isinstance(modules, SplintModule):
            return [modules]
        if isinstance(modules, list) and all(isinstance(m, SplintModule) for m in modules):
            return modules
        raise SplintException('Modules must be a list of SplintModule objects.')

    @staticmethod
    def _process_check_funcs(check_functions: List[SplintFunction] | None) -> List[SplintFunction]:
        """ Load up an arbitrary list of splint functions.
        These functions are tagged with adhoc for module"""
        if isinstance(check_functions, list) and len(check_functions) >= 1:
            for count, f in enumerate(check_functions, start=1):
                if not isinstance(f, SplintFunction):
                    raise SplintException(
                        "Functions must be a list of SplintFunction objects."
                    )
                # Since we are building up a module from nothing we give it a generic name and
                # remember the load order.
                f.index = count
                f.module = "adhoc"
            return check_functions

        if not check_functions:
            return []

        raise SplintException("Functions must be a list of SplintFunction objects.")

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

    def prepare(self, filter_functions=None):
        """
        Prepare the collected functions for running checks.

        Run through the collected functions to prepare the checks that will be run.
        A list of filter functions may be provided to filter the functions. Filter
        functions must return True if the function should be kept.

        Args:
            filter_functions (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """

        # If no filter functions are provided then use a default one allows all functions
        filter_functions = filter_functions or [lambda _: True]

        self.auto_gen_ruids()

        # At this point we have all the functions in the packages, modules and functions
        # Now we need to filter out the ones that are not wanted. Filter functions return
        # True if the function should be kept
        self.collected = []
        for splint_func in self.pre_collected:
            if all(f(splint_func) for f in filter_functions):
                self.collected.append(splint_func)

        # Now use the RC file.  Note that if you are running filter functions AND
        # an RC file this can be confusing.  Ideally you use one or the other. but
        # it isn't an error to do so, you just need to know what you are doing.
        self.apply_rc(self.rc)

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

    def auto_gen_ruids(self, template='__ruid__@id@'):
        """ Provide a mechanism for to transition from no ruids to ruids.  This way they
            can only set up the rules that need rule_ids"""
        if not self.auto_ruid:
            return
        id_ = 1
        for function in self.pre_collected:
            if function.ruid == '':
                function.ruid = template.replace("@id@", f'{id_:04d}')
                id_ += 1

    def apply_rc(self, rc=None):
        """ Apply RC file to collected functions applying includes then excludes. """
        self.rc = rc or self.rc

        # By exiting early an NOT using the RC file we don't use
        # Sets as shown below.  Sets cause order to be nondeterministic
        if not self.rc:
            return self.collected

        self.collected = [function for function in self.collected
                          if self.rc.does_match(ruid=function.ruid,
                                                tag=function.tag,
                                                phase=function.phase,
                                                level=function.level)]

        return self.collected

    def exclude_by_attribute(self, tags: List[str] | str | None = None,
                             ruids: List[str] | str | None = None,
                             levels: List[int] | int | None = None,
                             phases: List[str] | str | None = None)->List[SplintFunction]:
        """ Run everything except the ones that match these attributes """

        # Make everything nice lists
        tags = _param_str_list(tags)
        ruids = _param_str_list(ruids)
        phases = _param_str_list(phases)
        levels = _param_int_list(levels)

        # Exclude attributes that don't match
        self.collected = [f for f in self.collected if f.tag not in tags and
                          f.ruid not in ruids and
                          f.level not in levels and
                          f.phase not in phases]
        return self.collected

    def include_by_attribute(self,
                             tags: List | str | None = None,
                             ruids: List | str | None = None,
                             levels: List | str | None = None,
                             phases: List | str | None = None)->List[SplintFunction]:
        """ Run everything that matches these attributes """

        # Make everything nice lists
        tags = _param_str_list(tags)
        ruids = _param_str_list(ruids)
        phases = _param_str_list(phases)
        levels = _param_int_list(levels)

        # This is a special case to make including everything the default
        if not tags and not ruids and not levels and not phases:
            return self.collected

        # Only include the attributes that match
        self.collected = [f for f in self.collected if (f.tag in tags) or
                          (f.ruid in ruids) or
                          (f.level in levels) or
                          (f.phase in phases)]
        
        return self.collected

    def load_environments(self):
        """
        THis takes the global environment and adds in the results
        from all the discovered environment functions.  The results
        are all merged into a dictionary of parameter names and their values.

        This works very much like pytest, only without the scoping Parameters
        that are needed in multiple places aren't regenerated.
        Returns:

        """

        # Prime the environment with top level config
        # This should be json-able things
        full_env = self.env.copy()

        for m in self.modules:
            for env_func in m.env_functions:
                # TODO: There should be exceptions on collisions
                full_env.update(env_func(full_env))

        # This is a concern, there should be no nulls, HOWEVER this is more complex
        # since there should be no nulls for parameters to the collected check functions.
        # for now, I'm tracking this and dumping it in the results.
        self.env_nulls = [key for key, value in full_env.items() if value is None]

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
        Return a list of all the levels in the collected functions.

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

    class AbortYieldException(Exception):
        """Allow breaking out of multi level loop without state variables"""

    def yield_all(self, env=None):
        """
        Yield all the results from the collected functions

        This is where the rule engine does its work.

        Args:
            env: The environment to use for the rule functions

        Yields:
            _type_: SplintResult
        """

        # Note that it is possible for the collected list to be
        # empty.  This is not an error condition.  It is possible
        # that the filter functions have filtered out all the
        # functions.
        count = 0
        self.progress_callback(count, self.function_count, "Start Rule Check")
        self.start_time = dt.datetime.now()

        try:

            env = self.load_environments()

            # Shuts up linter
            result: SplintResult | None = None
            function: SplintFunction | None = None

            # Count here to enable progress bars
            for count, function in enumerate(self.collected, start=1):

                # Lots of magic here
                function.env = env

                self.progress_callback(count,
                                       self.function_count,
                                       f"Func Start {function.function_name}")
                for result in function():
                    yield result

                    # Check early exits
                    if self.abort_on_fail and result.status is False:
                        raise self.AbortYieldException()

                    if self.abort_on_exception and result.except_:
                        raise self.AbortYieldException()

                    # Stop yielding from a function
                    if function.finish_on_fail and result.status is False:
                        self.progress_callback(count, self.function_count,
                                               f"Early exit. {function.function_name} failed.")
                        break
                    self.progress_callback(count, self.function_count, "", result)
                self.progress_callback(count, self.function_count, "Func done.")

        except self.AbortYieldException:
            name = function.function_name if function is not None else "???"

            if self.abort_on_fail:
                self.progress_callback(count,
                                       self.function_count,
                                       f"Abort on fail: {name}")
            if self.abort_on_exception:
                self.progress_callback(count,
                                       self.function_count,
                                       f"Abort on exception: {name}")

        self.end_time = dt.datetime.now()
        self.progress_callback(count,
                               self.function_count,
                               "Rule Check Complete.")

    def run_all(self, env=None):
        """
        List version of yield all.

        """

        # A deceptively important line of code
        self.results = list(self.yield_all(env=env))

        self.score = self.score_strategy(self.results)
        self.progress_callback(self.function_count,
                               self.function_count,
                               f"Score = {self.score:.1f}")
        return self.results

    @property
    def clean_run(self):
        """ No exceptions """
        return all(not r.except_ for r in self.results)

    @property
    def perfect_run(self):
        """No fails or skips"""
        return all(r.status and not r.skipped and not r.warn_msg for r in self.results)

    @property
    def skip_count(self):
        """Number of skips"""
        return len([r for r in self.results if r.skipped])

    @property
    def warn_count(self):
        """Number of warns"""
        return len([r for r in self.results if r.warn_msg])

    @property
    def pass_count(self):
        """Number of passes"""
        return len([r for r in self.results if r.status and not r.skipped])

    @property
    def fail_count(self):
        """Number of fails"""
        return len([r for r in self.results if not r.status and not r.skipped])

    @property
    def result_count(self):
        """ Possibly redundant call to get the number of results."""
        return len(self.results)

    @property
    def function_count(self):
        """ Count all the collected functions (this is not the ones that are run)"""
        return len(self.collected)

    @property
    def module_count(self):
        """Count up all the modules in all the packages"""
        return len(self.modules) + sum(1 for pkg in self.packages for _ in pkg.modules)

    @property
    def module_names(self):
        """Get a list of module names."""
        return [module.name for module in self.modules] + \
            [m.module_name for pkg in self.packages for m in pkg.modules]

    @property
    def package_count(self):
        """ Count of the packages (almost always 1 or 0)"""
        return len(self.packages)

    def get_header(self) -> dict:
        """Make a header with the top level information about the checker run"""
        header = {
            "package_count": self.package_count,
            "module_count": self.module_count,
            "modules": self.module_names,
            "function_count": self.function_count,
            "tags": self.tags,
            "levels": self.levels,
            "phases": self.phases,
            "ruids": self.ruids,
            "score": self.score,
            "env_nulls": self.env_nulls,
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
            "total_count": self.result_count,

            # the meat of the output lives here
            "results": [r.as_dict() for r in self.results],
        }
        return h | r
