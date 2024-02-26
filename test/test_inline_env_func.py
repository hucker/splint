import pytest
import src.splint as splint

@pytest.fixture
def para_env():
    return splint.SplintModule(module_name="check_env",module_file="para_env/check_env.py")


def test_inline_env_func(para_env):
    assert len(para_env.env_functions)==1

    ch = splint.SplintChecker(modules=[para_env],env={"global_env":"hello"},auto_setup=True)
    results = ch.run_all()
    assert len(results) == 15
    assert all((result.status for result in results))