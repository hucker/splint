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


def test_score_by_result(by_func_weights_with_skip):

    # Setup the 3 strategies
    by_result = splint.ScoreByResult()


    # By result, it is easy to just add with code
    total_weight = 2 * 100 + 1*200 + 2*300
    total_pass = 1*200 + 1*300
    score =100.0*(total_pass*1.0 / total_weight*1.0)
    assert by_result.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_result(by_func_weights_with_skip) == pytest.approx(score)



def test_score_by_function_binary(by_func_weights_with_skip):

    by_function_binary = splint.ScoreByFunctionBinary()
     # for the binary function case I'll do it by hand.  There are 3 functions with 3 different weights
    total_weight = 100 + 200 + 300  # weights for 3 functions
    total_pass = 0 * 100 +  1 * 200 + 0 * 300

    score = 100.0*(total_pass / total_weight)

    assert by_function_binary.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_binary(by_func_weights_with_skip) == pytest.approx(score)

def test_score_by_function_mean(by_func_weights_with_skip):

    by_function_mean = splint.ScoreByFunctionMean()

    # for the mean function case I'll do it by hand.  There are 3 functions with 3 different weights
    total_weight = (2*100) + (1*200) + (2*300)  # weights for 3 functions
    total_pass = (0/2*100) + (1*200) + (1 * 300)
    score =100.0*(total_pass*1.0 / total_weight*1.0)
    assert by_function_mean.score(by_func_weights_with_skip) == pytest.approx(score)
    assert by_function_mean(by_func_weights_with_skip) == pytest.approx(score)


def test_strategy_factory_text():
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_function_mean"),splint.ScoreByFunctionMean)
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_function_binary"),splint.ScoreByFunctionBinary)
    assert isinstance(splint.ScoreStrategy.strategy_factory("by_result"),splint.ScoreByResult)

def test_strategy_factory_class_name():
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreByFunctionMean"),splint.ScoreByFunctionMean)
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreByFunctionBinary"),splint.ScoreByFunctionBinary)
    assert isinstance(splint.ScoreStrategy.strategy_factory("ScoreByResult"),splint.ScoreByResult)

def test_strategy_factory_class():
    assert isinstance(splint.ScoreStrategy.strategy_factory(splint.ScoreByFunctionMean),splint.ScoreByFunctionMean)
    assert isinstance(splint.ScoreStrategy.strategy_factory(splint.ScoreByFunctionBinary),splint.ScoreByFunctionBinary)
    assert isinstance(splint.ScoreStrategy.strategy_factory(splint.ScoreByResult),splint.ScoreByResult)