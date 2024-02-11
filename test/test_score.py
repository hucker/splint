import src.splint as splint
import pytest


@pytest.fixture
def all_pass():
    return [
        splint.SR(status=True, msg="No RUID", func_name="func1"),
        splint.SR(status=True, msg="No RUID", func_name="func2"),
        splint.SR(status=True, msg="No RUID", func_name="func3"),
    ]


@pytest.fixture
def all_fail():
    return [
        splint.SR(status=False, msg="No RUID", func_name="func1"),
        splint.SR(status=False, msg="No RUID", func_name="func2"),
        splint.SR(status=False, msg="No RUID", func_name="func3"),
    ]


@pytest.fixture
def one_quarter_pass():
    return [
        splint.SR(status=True, msg="No RUID", func_name="func1"),
        splint.SR(status=False, msg="No RUID", func_name="func2"),
        splint.SR(status=False, msg="No RUID", func_name="func3"),
        splint.SR(status=False, msg="No RUID", func_name="func4"),
    ]


def test_simple_score_pass(all_pass):
    strat = splint.ScoreByResultSimple()
    assert strat.score(all_pass) == 100.0


def test_simple_score_fail(all_fail):
    strat = splint.ScoreByResultSimple()
    assert strat.score(all_fail) == 0.0


def test_simple_score_fraction(one_quarter_pass):
    strat = splint.ScoreByResultSimple()
    assert strat.score(one_quarter_pass) == 25.0


@pytest.fixture
def by_func():
    return [
        splint.SR(status=False, msg="No RUID", func_name="func1"),
        splint.SR(status=False, msg="No RUID", func_name="func1"),
        splint.SR(status=True, msg="No RUID", func_name="func2"),
        splint.SR(status=True, msg="No RUID", func_name="func2"),
        splint.SR(status=False, msg="No RUID", func_name="func3"),
        splint.SR(status=True, msg="No RUID", func_name="func3"),
    ]


def test_by_func(by_func):
    # All functions are considered equally important
    strat = splint.ScoreByResultSimple()
    assert strat.score(by_func) == 50.0


def test_by_simple_func(by_func):
    # All individual function results must pass for a pass
    strat = splint.ScoreSimpleFunction()
    # Only func2 has both values passing
    assert strat.score(by_func) == pytest.approx(33.333333)


@pytest.fixture
def by_func_weights():
    # NOTE: The weight value must be the same for each function.
    return [
        splint.SR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        splint.SR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        splint.SR(status=True, msg="No RUID", func_name="func2", weight=200.0),
        splint.SR(status=True, msg="No RUID", func_name="func2", weight=200.0),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0),
    ]

def test_by_weighted_simple_func(by_func_weights):
    # With this strategy, the weight is applied to the score only if ALL tests
    # pass for a given function.
    strat = splint.ScoreSimpleWeightFunction()

    # This strategy requires all to pass for a pass and then weight is applied

    # Only func2 has both values passing
    assert strat.score(by_func_weights) == pytest.approx(33.33333)


def test_by_weighted_func(by_func_weights):
    # With this strategy, the weight is applied to the score only if ALL tests
    # pass for a given function.
    strat = splint.ScoreWeightedFunction()

    # This stratege handles individual results and weights.  THis allows a function
    # to fail by a percentage rather than all or nothing.  In the above
    # example 3 tests pass with a total weight of 700.  The total weight is 1200
    # so the score is 58.333333.

    # Only func2 has both values passing
    pass_weight = sum([sr.weight for sr in by_func_weights if sr.status])
    weight= sum([sr.weight for sr in by_func_weights])


    assert strat.score(by_func_weights) == pytest.approx(pass_weight/weight*100.0)


@pytest.fixture
def by_func_weights_with_skip():
    # NOTE: The weight value must be the same for each function.
    return [
        splint.SR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        splint.SR(status=False, msg="No RUID", func_name="func1", weight=100.0),
        splint.SR(status=True, msg="No RUID", func_name="func2", weight=200.0),
        splint.SR(status=True, msg="No RUID", func_name="func2", weight=200.0,skipped=True),
        splint.SR(status=False, msg="No RUID", func_name="func3", weight=300.0),
        splint.SR(status=True, msg="No RUID", func_name="func3", weight=300.0),
    ]

def test_by_weighted_func_with_skip(by_func_weights_with_skip):
    # With this strategy, the weight is applied to the score only if ALL tests
    # pass for a given function.
    strat = splint.ScoreWeightedFunction()

    # This stratege handles individual results and weights.  THis allows a function
    # to fail by a percentage rather than all or nothing.  In the above
    # example 3 tests pass with a total weight of 700.  The total weight is 1200
    # so the score is 58.333333.

    # Only func2 has both values passing
    pass_weight = sum([sr.weight for sr in by_func_weights_with_skip if sr.status and not sr.skipped])
    weight= sum([sr.weight for sr in by_func_weights_with_skip if sr.skipped is False])


    assert strat.score(by_func_weights_with_skip) == pytest.approx(pass_weight/weight*100.0)