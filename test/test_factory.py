"""
These the rc factory method allowing fairly easily to have various flavors or RC files to be
be interchangable.

"""

import pytest

from splint import splint_rc_factory,SplintException


def test_factory():
    rc_dict = {'package1': {'ruids': 'r1 -r2',
                  'tags': 't1 -t2',
                  'phases': 'p1 -p2'}}


    rc1 = splint_rc_factory(param='./rc_files/good.json',section='package1')
    rc2 = splint_rc_factory(param='./rc_files/good.toml',section='package1')
    rc3 = splint_rc_factory(param=rc_dict,section='package1')
    rc4 = splint_rc_factory(param=rc_dict['package1'])

    assert rc1.tags == rc2.tags == rc3.tags == rc4.tags == ['t1']
    assert rc1.ruids == rc2.ruids == rc3.ruids == rc4.ruids == ['r1']
    assert rc1.phases == rc2.phases == rc3.phases == rc4.phases == ['p1']
    assert rc1.ex_tags == rc2.ex_tags == rc3.ex_tags == rc4.ex_tags == ['t2']
    assert rc1.ex_ruids == rc2.ex_ruids == rc3.ex_ruids == rc4.ex_ruids == ['r2']
    assert rc1.ex_phases == rc2.ex_phases == rc3.ex_phases == rc4.ex_phases == ['p2']


@pytest.mark.parametrize("param", [
    # Factory class expects a file name or a dictionary
    "foo.txt",
    1,
    [],
    set(),
    ()
    # Add more test cases as needed
])
def test_factory_exception(param):
    with pytest.raises(SplintException):
        _ = splint_rc_factory(param=param, section='')