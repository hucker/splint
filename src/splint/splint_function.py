import functools
import inspect
import logging
import re
import time
import traceback
from typing import Generator

from .splint_attribute import get_attribute
from .splint_exception import SplintException
from .splint_result import SplintResult


def result_hook_fix_blank_msg(sfunc, result: SplintResult) -> SplintResult:
    """Fix the message of a result if it is blank.

    This is an example of a result hook used by splint to write
    a useful message if the user did not provide one.

    Args:
        result (SplintResult): The result to rewrite.

    Returns:
        SplintResult: The result with the message fixed.
    """
    # If the result has no message, then create a default one either
    # from the doc string or from the function name/module/package/repo.
    if not result.msg:
        if sfunc.doc.strip().count("\n") == 0 and sfunc.doc.strip():
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
            result.msg = f"Ran {msg_str} {sfunc.function}.{result.count:03d}"
    return result


def result_hook_warn_to_fail(_, result: SplintResult) -> SplintResult:
    """If a warning message is provided change the status to fail

    Args:
        result (SplintResult): The result to rewrite.

    Returns:
        SplintResult: The result with the message fixed.
    """
    if result.warn_msg:
        result.status = False
    return result


class SplintFunction:
    """
    A class to represent a function in a module for the Splint framework.

    This class stores a function and its associated module, and allows the function to be called with
    error handling.

    All functions returning values are converted to generators that yield SplintResult objects.
    This allows functions to return multiple results and for the user not to worry about the
    difference between functions that return a single result and functions returning multiple results.

    Ideally people would just use generators everywhere, but this allows them to be lazy and just
    return a single result and have it be converted to a generator.

    Attributes:
        module (ModuleType): The module that contains the function.
        function (Callable): The function to be called.
        parameters (inspect.Parameters): The parameters of the function.
        allowed_exceptions (Tuple[Type[Exception]]): The types of exceptions to catch when calling the function.

    Methods:
        __str__(): Returns a string representation of the SplintFunction.
        __call__(*args, **kwds): Calls the stored function and collects information about the result.
    """

    def __init__(
        self,
        module,
        function,
        allowed_exceptions=None,
        env=None,
        pre_sr_hooks=None,
        post_sr_hooks=None,
    ):
        self.env = env or {}
        self.module = module
        self.function = function
        self.is_generator = inspect.isgeneratorfunction(function)
        self.function_name = function.__name__

        # Using inspect gets the docstring without the python indent.
        self.doc = inspect.getdoc(function)

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

        # Get function attributes, using defaults if the user did not specify attributes.
        self.tag = get_attribute(function, "tag")
        self.level = get_attribute(function, "level")
        self.phase = get_attribute(function, "phase")
        self.weight = get_attribute(function, "weight")
        self.skip = get_attribute(function, "skip")
        self.suid = get_attribute(function, "suid")

        logging.debug("Loaded function %s", self)
        self.allowed_exceptions = allowed_exceptions or (Exception,)

    def __str__(self):
        return f"SplintFunction({self.function=},{self.parameters=})"

    def _get_parameter_values(self):
        args = []
        for param in self.parameters.values():
            if param.name in self.env:
                args.append(self.env[param.name])
            elif param.default != inspect.Parameter.empty:
                args.append(param.default)
            else:
                print("???")
        return args

    def __call__(self, *args, **kwds) -> Generator[SplintResult, None, None]:
        """Call the user provided function and collect information about the result.

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

        # It is possible for an exception to occur before the generator is created.
        # so we need a value to be set for count.
        count = 1

        try:

            # This allows for returning a single result using return or
            # multiple results returning a list of results.
            if not self.is_generator:
                # If the function is not a generator, then just call it
                results = self.function(*args)
                end_time = time.time()
                if isinstance(results, SplintResult):
                    results = [results]

                # TODO: I could not make a decorator work for this, so I just put it here.
                elif isinstance(results, bool):
                    results = [SplintResult(status=results)]
                for count, r in enumerate(results, start=1):
                    # TODO: Time is wrong here, we should estimate each part taking 1/count of the total time
                    r = self.load_result(r, start_time, end_time, count=1)
                    yield r

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
                    start_time = time.time()

        except self.allowed_exceptions as e:
            result = SplintResult(status=False)
            result = self.load_result(result, 0, 0, count)
            result.except_ = e
            result.traceback = traceback.format_exc()
            mod_msg = "" if not self.module else f"{self.module}"
            result.msg = f"Exception '{e}' occurred while running {mod_msg}{self.function.__name__}"
            yield result

    def _get_section(self, header="", text=None):
        """
        Extracts a section from the docstring based on the provided header.
        If no header is provided, it returns the text before the first header.
        If the header is provided, it returns the text under that header.
        If the header isn't found, it returns the text before the first header.

        Parameters:
        header (str): The header of the section to extract.
        text (str): INternally this is never used, but is useful for testing.

        Returns:
        str: The text of the requested section.
        """

        text = text or self.doc

        # Split the docstring into sections
        sections = re.split(r"(\w+:)", self.doc)

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
        Provide a bunch of metadata about the function call.

        An important design decision was made to make the result data not be hierarchical.
        because there are different possible hierarchies.  Instead the result data is flat
        with attributes that can be used to filter and sort the results to achieve the desired
        hierarchy.
        """
        # Use getattr to avoid repeating the same pattern of checking if self.module exists
        result.pkg_name = getattr(self.module, "__package__", "")
        result.module_name = getattr(self.module, "__name__", "")

        # Assign the rest of the attributes directly
        result.func_name = self.function_name
        result.doc = self.doc
        result.tag = self.tag
        result.level = self.level
        result.phase = self.phase
        result.runtime_sec = end_time - start_time
        result.count = count

        # Apply all of the hooks to the result
        for hook in self.result_hooks:
            if result is not None:
                result = hook(self, result)

        return result
