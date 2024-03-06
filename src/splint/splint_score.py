"""Basic scoring algorithms for Splint test results. """

import abc
from typing import List

from .splint_exception import SplintException
from .splint_result import SplintResult


class ScoreStrategy(abc.ABC):
    """
    A strategy for scoring the results of a Splint run.
    It is assumed that many scoring strategies could be implemented, this provides a way
    for those strategies to be implemented in code (by providing a class) or from file
    by providing a name that matches the class strat_name attribute.
    """

    strategy_name = None

    @abc.abstractmethod
    def score(self, results: List[SplintResult] = None): # pragma: no cover
        pass

    def __call__(self, results: List[SplintResult] = None):
        return self.score(results)

    @classmethod
    def strategy_factory(cls, strategy_name_or_class) -> "ScoreStrategy":
        """Make a strategy object from a name or class.  This will be read from files or code, so they support both"""
        if isinstance(strategy_name_or_class, str):
            # Note this only goes one level deep in subclasses, which for now is good enough.
            for subclass in cls.__subclasses__():
                if (
                        subclass.strategy_name == strategy_name_or_class
                        or subclass.__name__ == strategy_name_or_class
                ):
                    return subclass()
            raise SplintException(
                f"No scoring strategy with name '{strategy_name_or_class}' found."
            )
        elif issubclass(strategy_name_or_class, cls):
            return strategy_name_or_class()
        else:
            raise SplintException(
                "Argument must be a strategy name or a ScoreStrategy subclass."
            )


class ScoreByResult(ScoreStrategy):
    """Calculate the score by individually weighting each result"""

    strategy_name = "by_result"

    def score(self, results: List[SplintResult] = None):
        """Weighted result of all results."""
        weight_sum = 0
        passed_sum = 0
        # Remove any skipped results
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0
            #raise SplintException("No results to score.")

        for result in results:
            passed_sum += result.weight if result.status else 0
            weight_sum += result.weight

        return (100.0 * passed_sum) / (weight_sum * 1.0)


class ScoreByFunctionBinary(ScoreStrategy):
    """Calculate the score by requiring ALL results from a function to be pass to consider the function passed."""

    strategy_name = "by_function_binary"

    def score(self, results: List[SplintResult] = None):
        """If any result on a function fails then the function fails."""

        score_functions = {}

        for result in results:
            key = f"{result.pkg_name}.{result.module_name}.{result.func_name}".lstrip(
                "."
            )
            score_functions.setdefault(key, []).append(result)

        # Remove any skipped results
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0

        for key, results in score_functions.items():
            if not results:
                score_functions[key] = 0.0
            else:
                score_functions[key] = 100.0 if all(r.status for r in results) else 0.0

        # The score should be the average of the scores for each function
        return sum(score_functions.values()) / (len(score_functions) * 1.0)


class ScoreByFunctionMean(ScoreStrategy):
    """Calculate score by averaging the results from a function.  This means that a function could 50% pass"""

    strategy_name = "by_function_mean"

    def score(self, results: List[SplintResult] = None):
        """Find the average of the results from each function."""

        function_results = {}

        # Remove any skipped results
        results = [result for result in results if not result.skipped]
        if not results:
            return 0.0

        for result in results:
            key = f"{result.pkg_name}.{result.module_name}.{result.func_name}".lstrip(
                "."
            )
            function_results.setdefault(key, []).append(result)

        sum_weights = 0
        sum_passed = 0

        # Now we have a dictionary of results for each function.  We can now score each function
        for key, results in function_results.items():
            for result in results:
                sum_weights += result.weight
                sum_passed += result.weight if result.status else 0

        if sum_weights == 0:
            raise SplintException("The sum of weights is 0.  This is not allowed.")

        # The score should be the average of the scores for each function
        return (100.0 * sum_passed) / (sum_weights * 1.0)


class ScoreBinaryFail(ScoreStrategy):
    """Anything fails then the test is a fail.  Empty results fail."""
    strategy_name = "by_binary_fail"

    def score(self, results: List[SplintResult]) -> float:
        if not results:
            return 0.0
        if any(not result.status for result in results if not result.skipped):
            return 0.0
        return 100.0


class ScoreBinaryPass(ScoreStrategy):
    """Anything passes then the test is a pass. Empty results fail. """
    strategy_name = "by_binary_pass"

    def score(self, results: List[SplintResult]) -> float:
        if any(result.status for result in results if not result.skipped):
            return 100.0
        return 0.0
