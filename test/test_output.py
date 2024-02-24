import pytest

import src.splint as splint


@pytest.fixture
def simple1():
    @splint.attributes(tag="t1", level=1, ruid="ruid_1",phase='proto')
    def func1():
        """my doc string"""
        yield splint.SplintResult(status=True, msg="It works1")

    return splint.SplintFunction(func1)

@pytest.fixture
def simple2():
    @splint.attributes(tag="t2", level=2, ruid="ruid_2",phase='production')
    def func2():
        """my doc string"""
        yield splint.SplintResult(status=True, msg="It works2")

    return splint.SplintFunction(func2)


def test_json(simple1,simple2):
    """Test that the as_dict method serializes  nicely"""
    ch = splint.SplintChecker(functions=[simple1,simple2],auto_setup=True)
    results = ch.run_all()
    d = ch.as_dict()
    assert d['function_count'] == 2

    # Important to treat these as sets, don't assume order.
    assert set(d['levels']) == set([1,2])
    assert set(d['ruids']) == set(['ruid_1','ruid_2'])
    assert set(d['tags']) == set(['t1','t2'])
    assert set(d['phases']) == set(['proto','production'])
    assert set(d['functions']) == set(['func1','func2'])

    assert d['passed_count'] == 2
    assert d['failed_count'] == 0
    assert len(d['results']) == 2

    result = d['results'][0]
    assert result['status'] is True
    assert result['func_name'] == 'func1'
    assert result['msg'] == 'It works1'
    assert result['warn_msg'] == ''
    assert result['info_msg'] == ''
    assert result['tag'] == 't1'
    assert result['except_'] == 'None'    #Odd??
    assert result['traceback'] == ''
    assert result['skipped'] is False
    assert result['phase'] == 'proto'
    assert result['count'] == 1
    assert result['weight'] == 100
    assert result['ruid'] == 'ruid_1'
    assert result['ttl_minutes'] == 0.0
    assert result['mit_msg'] == ''
    assert result['doc'] == 'my doc string'
