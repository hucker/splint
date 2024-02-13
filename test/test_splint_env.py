"""
    Baseline tests for the envirnment module
"""
import src.splint as splint


def test_splint_enum():
    assert splint.SplintEnvScope.REPO.value == 4
    assert splint.SplintEnvScope.PACKAGE.value == 3
    assert splint.SplintEnvScope.MODULE.value == 2
    assert splint.SplintEnvScope.FUNCTION.value == 1


    assert splint.SplintEnvScope.REPO.name == "REPO"
    assert splint.SplintEnvScope.PACKAGE.name == "PACKAGE"
    assert splint.SplintEnvScope.MODULE.name == "MODULE"
    assert splint.SplintEnvScope.FUNCTION.name == "FUNCTION"

def test_splint_gt_cmp():
    assert splint.SplintEnvScope.REPO.value > splint.SplintEnvScope.PACKAGE.value
    assert splint.SplintEnvScope.PACKAGE.value > splint.SplintEnvScope.MODULE.value
    assert splint.SplintEnvScope.MODULE.value > splint.SplintEnvScope.FUNCTION.value
    assert splint.SplintEnvScope.REPO.value > splint.SplintEnvScope.MODULE.value

def test_splint_lt_cmp():
    assert splint.SplintEnvScope.PACKAGE.value < splint.SplintEnvScope.REPO.value
    assert splint.SplintEnvScope.MODULE.value < splint.SplintEnvScope.PACKAGE.value
    assert splint.SplintEnvScope.FUNCTION.value < splint.SplintEnvScope.MODULE.value
    assert splint.SplintEnvScope.MODULE.value < splint.SplintEnvScope.REPO.value

def test_make_constant_function():
    func = splint.make_constant_function("test", 1)
    assert func() == 1
    assert func.__name__ == "test"  # noqa: F821

def test_splint_env_function():
    def func():
        return 1
    sef = splint.SplintEnvFunction("test", splint.SplintEnvScope.REPO, func)
    assert sef.name == "test"
    assert sef.scope == splint.SplintEnvScope.REPO
    assert sef.function == func
    assert sef.value is None
    assert sef.ready is False
    assert sef.force_immutable is True

    sef.setup(splint.SplintEnvScope.REPO)
    assert sef.ready is True
    assert sef.value == 1

    sef.teardown(splint.SplintEnvScope.REPO)
    assert sef.ready is False
    assert sef.value is None



GLOBAL_SETUP_TEARDOWN_TRACKER = 0

def test_splint_env_gen():
    def gen_func():
        global GLOBAL_SETUP_TEARDOWN_TRACKER
        GLOBAL_SETUP_TEARDOWN_TRACKER = 1
        yield GLOBAL_SETUP_TEARDOWN_TRACKER
        GLOBAL_SETUP_TEARDOWN_TRACKER = 0

    sef = splint.SplintEnvFunction("test", splint.SplintEnvScope.REPO, gen_func)
    assert sef.name == "test"
    assert sef.scope == splint.SplintEnvScope.REPO
    assert sef.function == gen_func
    assert sef.value is None
    assert sef.ready is False
    assert sef.force_immutable is True

    sef.setup(splint.SplintEnvScope.REPO)
    assert sef.ready is True
    assert sef.value == 1
    assert GLOBAL_SETUP_TEARDOWN_TRACKER == 1

    sef.teardown(splint.SplintEnvScope.REPO)
    assert sef.ready is False
    assert sef.value is None
    assert GLOBAL_SETUP_TEARDOWN_TRACKER == 0
