import time
import inspect
import traceback
import logging
import functools

from .splint_result import SplintResult
from .splint_attribute import get_attribute



class SplintFunction:
    """
    A class to represent a function in a module for the Splint framework.

    This class stores a function and its associated module, and allows the function to be called with error handling.

    All functions that return values are converted to generators that yield SplintResult objects.  This allows
    functions to return multiple results and for the user not to have to worry about the difference between
    functions that return a single result and functions that return multiple results.

    Ideally people would just use generators everywhere, but this allows them to be lazy and just return a single
    result and have it be converted to a generator.

    Attributes:
        module (ModuleType): The module that contains the function.
        function (Callable): The function to be called.
        parameters (inspect.Parameters): The parameters of the function.
        allowed_exceptions (Tuple[Type[Exception]]): The types of exceptions to catch when calling the function.

    Methods:
        __str__(): Returns a string representation of the SplintFunction.
        __call__(*args, **kwds): Calls the stored function and collects information about the result.
    """
    def __init__(self, module,function,allowed_exceptions=None):
        self.module = module
        self.function = function
        self.function_name = function.__name__
        self.doc = inspect.getdoc(function)
        self.parameters = inspect.signature(function).parameters
        self.is_generator = inspect.isgeneratorfunction(function)

        # Get funciton attributes, using defaults if the user did not specify attributes.
        self.tag = get_attribute(function, 'tag')
        self.level = get_attribute(function, 'level')
        self.phase = get_attribute(function, 'phase')
        self.weight = get_attribute(function, 'weight')
        self.skip = get_attribute(function, 'skip')
        logging.debug("Loaded function %s", self)
        self.allowed_exceptions = allowed_exceptions or (Exception,)

    def __str__(self):
        return f"SplintFunction({self.function=},{self.parameters=})"

    def get_parameter_values(self):
       return [],{}


    def __call__(self, *args, **kwds) -> SplintResult:
        """Call the user provided function and collect information about the result.

        Raises:
            SplintException: Exceptions are remapped to SplintExceptions for easier handling

        Returns:
            SplintResult: _description_

        Yields:
            Iterator[SplintResult]: _description_
        """
        # Call the stored functon and collect information about the result
        start_time = time.time()
        # Function returns a generator that needs to be iterated over
        args, kwds = self.get_parameter_values()
        try:
            # It is possible for an exception to occur before the generator is created.
            # so we need a value to be set for count.
            count = 1

            # This allows for returning a single result using return or
            # multiple results returning a list of results.
            if not self.is_generator:
                # If the function is not a generator, then just call it
                results = self.function(*args,**kwds)
                end_time = time.time()
                if isinstance(results,SplintResult):
                    results = [results]

                # TODO: This should be in a decorator
                elif isinstance(results,bool):
                    results = [SplintResult(status=results)]
                for count,r in enumerate(results,start=1):
                    r = self.load_result(r,start_time,end_time,count=1)
                    yield r
                return

            # Since functions can return multiple results, we keep track of them
            # with a count attribute.  THis is helpful for reporting.
            for count,result in enumerate(self.function(*args,**kwds),start=1):
                end_time = time.time()

                #TODO: This should be in a decorator
                if isinstance(result,bool):
                    result = SplintResult(status=result)

                result = self.load_result(result,start_time,end_time,count)

                yield result
                start_time = time.time()

        except self.allowed_exceptions as e:
            result = SplintResult(status=False)
            result = self.load_result(result,0,0,count)
            result.except_ = e
            result.traceback = traceback.format_exc()
            mod_msg = "" if not self.module else f"{self.module}"
            result.msg = f"Exception '{e}' occurred while running {mod_msg}{self.function.__name__}"
            yield result

    def load_result(self,result:SplintResult,start_time,end_time,count=1):
        """
        Provide a bunch of metadata about the function call.

        An important design decision was made to make the result data not be hierarchical.
        because there are different possible hierarchies.  Instead the result data is flat
        with attributes that can be used to filter and sort the results to achieve the desired
        hierarchy.


        """
        #result.module = self.module
        result.pkg_name = self.module.__package__ if self.module else ''
        result.module_name = self.module.__name__ if self.module else ''
        #result.function = self.function
        result.func_name = self.function_name
        result.doc = self.doc
        result.tag = self.tag
        result.level = self.level
        result.phase = self.phase
        result.runtime_sec = end_time - start_time
        result.count = count        # If the result has no message, then create a default one.
        if result.msg == "":
            if self.doc.strip().count("\n") == 0 and self.doc.strip() != "":
                result.msg = f"{result.func_name}{self.doc.strip()}"
            else:
                tag_str = f" tag={self.tag}" if self.tag else ""
                level_str = f" level={self.level}" if self.level else ""
                phase_str = f" phase={self.phase}" if self.phase else ""
                module_str = f" module={self.module}." if self.module else ""
                result.msg = f"Ran {module_str}{self.function}.{result.count:03d}{tag_str}{level_str}{phase_str}"
        return result