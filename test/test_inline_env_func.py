import pytest

from src import splint


@pytest.fixture
def para_env():
    return splint.SplintModule(module_name="check_env", module_file="para_env/check_env.py")


def test_inline_env_func(para_env):
    assert len(para_env.env_functions) == 1

    ch = splint.SplintChecker(modules=[para_env], env={"global_env": "hello"}, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 15
    assert all((result.status for result in results))


def test_module_not_in_list(para_env):
    assert len(para_env.env_functions) == 1

    ch = splint.SplintChecker(modules=para_env, env={"global_env": "hello"}, auto_setup=True)
    results = ch.run_all()
    assert len(results) == 15
    assert all((result.status for result in results))


def test_fail_on_none():
    @splint.attributes(tag="tag", phase="phase", level=1, weight=100, fail_on_none=True)
    def env_test_function(var):
        yield splint.SR(status=True, msg="This will pass if it ever gets here.")

    s_func = splint.SplintFunction(function=env_test_function)
    ch = splint.SplintChecker(check_functions=[s_func], env={'var': None}, auto_setup=True)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is False
    assert results[0].msg.startswith("Failed due to None argument 1 in func='env_test_function'")


def test_skip_on_none():
    @splint.attributes(tag="tag", phase="phase", level=1, weight=100, skip_on_none=True)
    def env_test_function(var):
        yield splint.SR(status=True, msg="This will pass if it ever gets here.")

    s_func = splint.SplintFunction(function=env_test_function)
    ch = splint.SplintChecker(check_functions=[s_func], env={'var': None}, auto_setup=True)
    results = ch.run_all()

    assert len(results) == 1
    assert results[0].status is None
    assert results[0].msg.startswith("Skipped due to None argument 1 in func='env_test_function'")
