""" The result of a splint run is a list of SplintResult objects.  These objects
    contain the results of the tests.  The results can be scored in a number of
    ways.  The simplest way is to score the results as a percentage of the total
    """

import pytest

import src.splint as splint


@pytest.fixture
def by_func_weights_with_skip():
    # NOTE: This gives a case than handles most of the edge case
    return [
        splint.SR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        splint.SR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        splint.SR(status=True, msg="No RUID", func_name="func2", weight=200.0),
        splint.SR(status=True, msg="No RUID", func_name="func2", weight=200.0, skipped=True),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0),
    ]

@pytest.fixture
def half_pass():
    # NOTE: This gives a case than handles most of the edge case
    return [
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0, skipped=True),
    ]

@pytest.fixture
def all_pass():
    # NOTE: This gives a case than handles most of the edge case
    return [
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0,skipped=True),
    ]

@pytest.fixture
def all_fail():
    # NOTE: This gives a case than handles most of the edge case
    return [
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0, skipped=True),
    ]


def test_score_by_result(by_func_weights_with_skip):
    # Set up the 3 strategies
    by_result = splint.ScoreByResult()

    # By result, it is easy to just add with code
    total_weight = 2 * 100 + 1 * 200 + 2 * 300
    total_pass = 1 * 200 + 1 * 300
    score = 100.0 * (total_pass * 1.0 / total_weight * 1.0)
    assert by_result.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_result(by_func_weights_with_skip) == pytest.approx(score)
    assert by_result([]) == 0.0


def test_score_by_function_binary(by_func_weights_with_skip):
    by_function_binary = splint.ScoreByFunctionBinary()
    # for the binary function case I'll do it by hand.  There are 3 functions with 3 different weights
    total_weight = 100 + 200 + 300  # weights for 3 functions
    total_pass = 0 * 100 + 1 * 200 + 0 * 300

    score = 100.0 * (total_pass / total_weight)

    assert by_function_binary.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_binary(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_binary.score([]) == 0.0


def test_score_by_function_mean(by_func_weights_with_skip):
    by_function_mean = splint.ScoreByFunctionMean()

    # for the mean function case I'll do it by hand.  There are 3 functions with 3 different weights
    total_weight = (2 * 100) + (1 * 200) + (2 * 300)  # weights for 3 functions
    total_pass = (0 / 2 * 100) + (1 * 200) + (1 * 300)
    score = 100.0 * (total_pass * 1.0 / total_weight * 1.0)
    assert by_function_mean.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_mean(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_mean([]) == 0.0

def test_score_binary_pass(all_pass,all_fail,half_pass):
    """Check that the full binary pass works"""
    by_binary_pass = splint.ScoreBinaryPass()
    assert by_binary_pass(all_pass) == 100.0
    assert by_binary_pass(all_fail) == 0.0
    assert by_binary_pass(half_pass) == 100
    assert by_binary_pass([]) == 0

def test_score_binary_fail(all_pass,all_fail,half_pass):
    """Check that the full binary fail works"""
    by_binary_fail = splint.ScoreBinaryFail()
    assert by_binary_fail(all_pass) == 100.0
    assert by_binary_fail(all_fail) == 0.0
    assert by_binary_fail(half_pass) == 0.0
    assert by_binary_fail([]) == 0

def test_strategy_factory_text():
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_function_mean"), splint.ScoreByFunctionMean)
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_function_binary"), splint.ScoreByFunctionBinary)
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_result"), splint.ScoreByResult)
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_binary_pass"), splint.ScoreBinaryPass)
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_binary_fail"), splint.ScoreBinaryFail)


def test_strategy_factory_class_name():
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreByFunctionMean"), splint.ScoreByFunctionMean)
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreByFunctionBinary"), splint.ScoreByFunctionBinary)
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreByResult"), splint.ScoreByResult)
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreBinaryPass"), splint.ScoreBinaryPass)
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreBinaryFail"), splint.ScoreBinaryFail)


