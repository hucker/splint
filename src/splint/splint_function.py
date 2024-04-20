"""
This class encapsulates the discovered rule functions found in the system.  A greate
deal of metadata is stored in the function and extracted from information about the function
its signature, its generator status etc.  This information is used so users do not need to
configure functions in multiple places.  Design elements from fastapi and pytest are obvious.
"""
import inspect
import re
import time
import traceback
from typing import Generator, List

from .splint_attribute import get_attribute
from .splint_exception import SplintException
from .splint_result import SplintResult


def result_hook_fix_blank_msg(sfunc: "SplintFunction",
                              result: SplintResult) -> SplintResult:
    """Fix the message of a result if it is blank.

    This is an example of a result hook used by splint to write
    a useful message if the user did not provide one.

    Args:
        result (SplintResult): The result to rewrite.

    Returns:
        SplintResult: The result with the message fixed.
    """
    # If the result has no message, then create a default one either
    # from the doc string or from the function name/module/package.
    if not result.msg:
        if sfunc.doc and sfunc.doc.strip().count("\n") == 0 and sfunc.doc.strip():
            result.msg = f"{result.func_name}{sfunc.doc.strip()}"
        else:
            # Use a dictionary to store the optional parts of the message
            # This makes it easier to add or remove parts in the future
            msg_parts = {
                "tag": sfunc.tag,
                "level": sfunc.level,
                "phase": sfunc.phase,
                "module": sfunc.module,
            }
            # Only include the parts that have a value
            msg_str = " ".join(
                f"{key}={value}" for key, value in msg_parts.items() if value
            )
            result.msg = f"Ran {sfunc.function_name}.{result.count:03d} {msg_str}"
    return result


ATTRIBUTES = ("tag", "level", "phase", "weight", "skip", "ruid", "skip_on_none",
              "fail_on_none", "ttl_minutes", "finish_on_fail")


class SplintFunction:
    """
        A class representing a function within the Splint framework's module.

        The class stores a function, its module and allows error-handled function calls.
        All functions returning values convert to generators yielding SplintResult objects.
        This ensures a consistent return type, eliminating the need to worry about
        functions returning multiple or single results.

        Ideal use is with generated generators, which attach useful attributes
        to each function. These attributes are then processed into the SplintFunction object.

        Attributes:
        - module (ModuleType): Contains the function.
        - function (Callable): Function to be called.
        - parameters (inspect.Parameters): Function parameters.
        - allowed_exceptions (Tuple[Type[Exception]]): Exception types for try-catch clauses.

        Methods:
        - __str__(): Returns string representation of SplintFunction.
        - __call__(*args, **kwds): Calls the function and gathers result info.
        """

    def __init__(self, function, module='',
                 allowed_exceptions=None,
                 env=None,
                 pre_sr_hooks=None,
                 post_sr_hooks=None):
        self.env = env or {}
        self.module = module
        self.function = function
        self.is_generator = inspect.isgeneratorfunction(function)
        self.function_name = function.__name__

        # Using inspect gets the docstring without the python indent.
        self.doc = inspect.getdoc(function) or ""

        self.parameters = inspect.signature(function).parameters
        self.result_hooks = [result_hook_fix_blank_msg]

        # Allow user to control rewriting the result hooks
        if isinstance(pre_sr_hooks, list):
            self.result_hooks = pre_sr_hooks + self.result_hooks
        elif pre_sr_hooks is None:
            pass
        else:
            raise SplintException("pre_sr_hooks must be a list")

        if isinstance(post_sr_hooks, list):
            self.result_hooks += post_sr_hooks
        elif post_sr_hooks is None:
            pass
        else:
            raise SplintException("post_sr_hooks must be a list")

        # This really should be a class rather than having to repeat yourself.
        self.tag = get_attribute(function, "tag")
        self.level = get_attribute(function, "level")
        self.phase = get_attribute(function, "phase")
        self.weight = get_attribute(function, "weight")
        self.skip = get_attribute(function, "skip")
        self.ruid = get_attribute(function, "ruid")
        self.skip_on_none = get_attribute(function, "skip_on_none")
        self.fail_on_none = get_attribute(function, "fail_on_none")
        self.ttl_minutes = get_attribute(function, "ttl_minutes")
        self.finish_on_fail = get_attribute(function, "finish_on_fail")

        # Support Time To Live using the return value of time.time.  Resolution of this
        # is on the order of 10e-6 depending on OS.  In my case this is WAY more than I
        # need, and I'm assuming you aren't building a trading system with this so you don't
        # care about microseconds.
        self.last_ttl_start = 0  # this will be compared to time.time() for ttl caching
        self.last_results: List[SplintResult] = []

        if self.weight in [True,False,None]:
            raise SplintException("Boolean and none types are not allowed for weights.")
        elif self.weight <= 0.0:
            raise SplintException("Weight must be greater than 0.0")

        self.allowed_exceptions = allowed_exceptions or (Exception,)

    def __str__(self):
        return f"SplintFunction({self.function_name=})"

    def _get_parameter_values(self):
        args = []
        for param in self.parameters.values():
            if param.name in self.env:
                args.append(self.env[param.name])
            elif param.default != inspect.Parameter.empty:
                args.append(param.default)

        return args

    def _cache_result(self, result):
        """Simple caching saves results if ttl_minutes is no 0"""
        if self.ttl_minutes:
            self.last_results.append(result)

    def __call__(self, *args, **kwds) -> Generator[SplintResult, None, None]:
        """Call the user provided function and collect information about the result.

        This is the heart of the system.  Each of these functions checks something
        in the system using the provided function and feedback.  Each function is
        a generator (or just a function that pretends to be a generator). This code
        manages the details that we'd prefer to handle in the core of the system
        rather than inside the check functions.

        Raises:
            SplintException: Exceptions are remapped to SplintExceptions for easier handling

        Returns:
            SplintResult:

        Yields:
            Iterator[SplintResult]:
        """
        # Call the stored function and collect information about the result
        start_time = time.time()

        # Function returns a generator that needs to be iterated over
        args = self._get_parameter_values()

        # If any arguments are None that is a bad thing.  That means that
        # a file could not be opened or other data is not available. If
        # Functions are not allowed to update the environment this only
        # needs to run once, rather than on every function call
        for count, arg in enumerate([arg for arg in args if arg is None], start=1):
            if self.fail_on_none:
                yield SplintResult(status=False,
                                   msg=f"Failed due to None argument {count} in func='{self.function_name}'|{self.ruid}",fail_on_none=True)
                return
            if self.skip_on_none:
                yield SplintResult(status=None, skipped=True,
                                   msg=f"Skipped due to None argument {count} in func='{self.function_name}|{self.ruid}'",skip_on_none=True)
                return

        # It is possible for an exception to occur before the generator is created.
        # so we need a value to be set for count.
        count = 1

        # If they want cacheing this takes care of it.
        if self.ttl_minutes * 60 + self.last_ttl_start > time.time():
            yield from self.last_results
            return

        try:
            self.last_results = []
            self.last_ttl_start = start_time

            # This allows for returning a single result using return or
            # multiple results returning a list of results.
            if not self.is_generator:
                # If the function is not a generator, then just call it
                results = self.function(*args)
                end_time = time.time()
                if isinstance(results, SplintResult):
                    results = [results]

                # TODO: I could not make a decorator work for this, so I just put it here.
                #       Ideally the attribute decorator could see a non generator function
                #       and wrap at creation rather than having this crap here.
                elif isinstance(results, bool):
                    results = [SplintResult(status=results)]
                if not isinstance(results[0], SplintResult):
                    raise SplintException(f"Invalid return from splint function {self.function_name}")
                for count, r in enumerate(results, start=1):
                    # TODO: Time is wrong here, we should estimate each part taking
                    #       1/count of the total time
                    r = self.load_result(r, start_time, end_time, count=1)
                    yield r

                    self._cache_result(r)

            else:
                # Functions can return multiple results, track them with a count attribute.
                for count, result in enumerate(self.function(*args, **kwds), start=1):
                    end_time = time.time()

                    if isinstance(result, bool):
                        result = SplintResult(status=result)
                    elif isinstance(result, list):
                        raise SplintException(
                            "Function yielded a list rather than a SplintResult or boolean"
                        )

                    result = self.load_result(result, start_time, end_time, count)

                    yield result

                    self._cache_result(result)

                    start_time = time.time()

        except self.allowed_exceptions as e:
            # Generically handle exceptions here so we can keep running.
            result = SplintResult(status=False)
            result = self.load_result(result, 0, 0, count)
            result.except_ = e
            result.traceback = traceback.format_exc()
            mod_msg = "" if not self.module else f"{self.module}"
            result.msg = f"Exception '{e}' occurred while running {mod_msg}.{self.function.__name__}"
            yield result

    def _get_section(self, header="", text=None):
        """
        Extracts a section from the docstring based on the provided header.
        If no header is provided, it returns the text before the first header.
        If the header is provided, it returns the text under that header.
        If the header isn't found, it returns the text before the first header.

        Parameters:
        header (str): The header of the section to extract.
        text (str): IInternally this is never used, but is useful for testing.

        Returns:
        str: The text of the requested section.
        """

        text = text or self.doc

        # Split the docstring into sections
        sections = re.split(r"(^\w+:)", text, flags=re.MULTILINE)

        # Just return the first line of the header
        if not header:
            return sections[0].strip().split("\n", 1)[0].strip()

        # Ensure the header ends with ':'
        header = header.strip() + ":" if not header.endswith(":") else header

        # Try to find the header and return the next section
        for i, section in enumerate(sections):
            if section.strip() == header:
                return sections[i + 1].strip()

        # If the header wasn't found, return the text before the first header
        return ""

    def load_result(self, result: SplintResult, start_time, end_time, count=1):
        """
        Provide a bunch of metadata about the function call, mostly hoisting
        parameters from the functon to the result.

        A design decision was made to make the result data flat since there are no more than
        1 possible hierarchy.  Tall-skinny.
        """
        # Use getattr to avoid repeating the same pattern of checking if self.module exists
        result.pkg_name = getattr(self.module, "__package__", "")
        result.module_name = getattr(self.module, "__name__", "")

        # Assign the rest of the attributes directly
        result.ruid = self.ruid
        result.func_name = self.function_name
        result.doc = self.doc
        result.tag = self.tag
        result.level = self.level
        result.phase = self.phase
        result.runtime_sec = end_time - start_time
        result.ttl_minutes = self.ttl_minutes
        result.count = count

        result.fail_on_none = self.fail_on_none
        result.skip_on_none = self.skip_on_none

        # Apply all (usually 1 or 0) hooks to the result
        for hook in self.result_hooks:
            if result is not None:
                result = hook(self, result)

        return result
