"""
These test the rc file classes.

This was built adhoc.  It c(sh)ould be setup to throughly test the
splint_rc code and then  the dictionaries used to initialize the
SplintRC class should be written off to JSON and TOML and then the
exact same tests should be run against the derived classes.

"""

import pytest

import splint
from splint import SplintException
from splint import splint_jsonrc
from splint import splint_rc
from splint import splint_tomlrc


def _test_invariants(rc: splint_rc.SplintRC):
    # the RC file has collections of values that
    # represent inclusions and exclusions.  These
    # sets should always intersect to an empty set.
    # This test could go ANYWHERE at any time and be true.
    assert set(rc.tags) & set(rc.ex_tags) == set()
    assert set(rc.ruids) & set(rc.ex_ruids) == set()
    assert set(rc.levels) & set(rc.ex_levels) == set()
    assert set(rc.phases) & set(rc.ex_phases) == set()


def test_base():
    """Test the base SplintRC class with single values for each attribute"""
    rc = splint_rc.SplintRC(display_name="empty")
    assert rc.display_name == "empty"
    assert not rc.tags
    assert not rc.ruids
    assert not rc.phases
    assert not rc.ex_tags
    assert not rc.ex_ruids
    assert not rc.ex_phases
    _test_invariants(rc)

    rc = splint_rc.SplintRC(display_name="Ruids", ruids=['ruid1', '-ruid2'])

    assert 'ruid1' in rc.ruids
    assert 'ruid2' in rc.ex_ruids
    assert not rc.ex_phases
    assert not rc.phases
    assert not rc.ex_tags
    assert not rc.tags
    _test_invariants(rc)

    rc = splint_rc.SplintRC(display_name="Phases", phases=['phase1', '-phase2'])

    assert 'phase1' in rc.phases
    assert 'phase2' in rc.ex_phases
    assert not rc.ex_tags
    assert not rc.tags
    assert not rc.ex_ruids
    assert not rc.ruids
    _test_invariants(rc)

    rc = splint_rc.SplintRC(display_name="Tags", tags=['tag1', '-tag2'])

    assert 'tag1' in rc.tags
    assert 'tag2' in rc.ex_tags
    assert not rc.ex_phases
    assert not rc.phases
    assert not rc.ex_ruids
    assert not rc.ruids
    _test_invariants(rc)

    rc = splint_rc.SplintRC(display_name="Levels", levels=['1', '-2'])

    assert '1' in rc.levels
    assert '2' in rc.ex_levels
    assert not rc.ex_phases
    assert not rc.phases
    assert not rc.ex_ruids
    assert not rc.ruids
    _test_invariants(rc)


def test_everything():
    """Test SplintRC initialization with all inputs as lists."""
    rc = splint_rc.SplintRC(display_name="FromList",
                            tags=['tag1', '-tag2', 'tag3'],
                            phases=['phase1', '-phase2', 'phase3'],
                            ruids=['ruid1', '-ruid2'],
                            levels=['1', '-2'])
    assert set(rc.tags) == {'tag1', 'tag3'}
    assert set(rc.ex_tags) == {'tag2'}
    assert set(rc.phases) == {'phase1', 'phase3'}
    assert set(rc.ex_phases) == {'phase2'}
    assert set(rc.ruids) == {'ruid1'}
    assert set(rc.ex_ruids) == {'ruid2'}
    assert set(rc.levels) == {'1'}
    assert set(rc.ex_levels) == {'2'}

    _test_invariants(rc)


def test_everything_as_string():
    """Test SplintRC initialization with all inputs as strings."""
    rc = splint_rc.SplintRC(display_name="FromString",
                            tags='tag1 -tag2',
                            phases='phase1 -phase2',
                            ruids='ruid1 -ruid2',
                            levels='1 2 -3')
    assert set(rc.tags) == {'tag1'}
    assert set(rc.ex_tags) == {'tag2'}
    assert set(rc.phases) == {'phase1'}
    assert set(rc.ex_phases) == {'phase2'}
    assert set(rc.ruids) == {'ruid1'}
    assert set(rc.ex_ruids) == {'ruid2'}
    assert set(rc.levels) == {'1', '2'}
    assert set(rc.ex_levels) == {'3'}

    # This test is really an invariant.
    assert set(rc.tags) & set(rc.ex_tags) == set()
    assert set(rc.ruids) & set(rc.ex_ruids) == set()
    assert set(rc.levels) & set(rc.ex_levels) == set()
    assert set(rc.phases) & set(rc.ex_phases) == set()
    _test_invariants(rc)


def test_everything_as_string2():
    """Test SplintRC initialization with more inputs as strings."""
    rc = splint_rc.SplintRC(display_name="FromString",
                            tags='tag1 -tag2 tag3',
                            phases='phase1 -phase2 phase3',
                            ruids='ruid1 -ruid2 ruid3')
    assert set(rc.tags) == {'tag1', 'tag3'}
    assert set(rc.ex_tags) == {'tag2'}
    assert set(rc.phases) == {'phase1', 'phase3'}
    assert set(rc.ex_phases) == {'phase2'}
    assert set(rc.ruids) == {'ruid1', 'ruid3'}
    assert set(rc.ex_ruids) == {'ruid2'}
    _test_invariants(rc)


def test_empty_string():
    rc = splint_rc.SplintRC(tags='')
    assert rc.tags == []
    assert rc.ex_tags == []

    rc = splint_rc.SplintRC(ruids='')
    assert rc.ruids == []
    assert rc.ex_ruids == []

    rc = splint_rc.SplintRC(phases='')
    assert rc.phases == []
    assert rc.ex_phases == []

    rc = splint_rc.SplintRC(levels='')
    assert rc.levels == []
    assert rc.ex_levels == []


def test_both_lists():
    attrs = ['a', 'b', 'c', '-c', '-d', '-e']
    with pytest.raises(SplintException, match=r'Attributes in list and exclusion'):
        _ = splint_rc.SplintRC(tags=attrs)

    with pytest.raises(SplintException, match=r'Attributes in list and exclusion'):
        _ = splint_rc.SplintRC(phases=attrs)

    with pytest.raises(SplintException, match=r'Attributes in list and exclusion'):
        _ = splint_rc.SplintRC(ruids=attrs)


def test_dups_in_lists():
    attrs = ['a', 'c', 'c', '-c', '-d', '-d']
    with pytest.raises(SplintException, match=r'Duplicate attributes'):
        _ = splint_rc.SplintRC(tags=attrs)

    with pytest.raises(SplintException, match=r'Duplicate attributes'):
        _ = splint_rc.SplintRC(phases=attrs)

    with pytest.raises(SplintException, match=r'Duplicate attributes'):
        _ = splint_rc.SplintRC(ruids=attrs)


@pytest.mark.parametrize("section", ['test1', 'test2'])
def test_toml(section):
    """Test SplintTomlRC with different sections from a TOML file."""
    rc = splint_tomlrc.SplintTomlRC(cfg='./rc_files/test.toml', section=section)
    assert 'ruid_foo' in rc.ruids
    assert 'ruid_bar' in rc.ruids
    assert 'ruid_baz' in rc.ex_ruids
    assert 'tag_spam' in rc.tags
    assert 'phase_alpha' in rc.phases
    assert 'phase_delta' in rc.ex_phases
    _test_invariants(rc)


@pytest.mark.parametrize("section", ['test1', 'test2'])
def test_json(section):
    """Test SplintJsonRC with different sections from a JSON file."""
    rc = splint_jsonrc.SplintJsonRC(cfg='./rc_files/test.json', section=section)
    assert 'ruid_foo' in rc.ruids
    assert 'ruid_bar' in rc.ruids
    assert 'ruid_baz' in rc.ex_ruids
    assert 'tag_spam' in rc.tags
    assert 'phase_alpha' in rc.phases
    assert 'phase_delta' in rc.ex_phases
    _test_invariants(rc)


@pytest.mark.parametrize(
    "tag_val, phase_val, ruid_val, level_val,msg",
    [
        ([], [], [], ['abc'], "Invalid integer value"),
        ([], [], [], 'abc', "Invalid integer value"),
        ([], [], [], '1 2 abc', "Invalid integer value"),
        ([], [], [], [1, 2, 'abc'], "Invalid integer value"),
    ],
)
def test_value_exceptions(tag_val, phase_val, ruid_val, level_val, msg):
    with pytest.raises(SplintException):
        _ = splint_rc.SplintRC(tags=tag_val, phases=phase_val, ruids=ruid_val, levels=level_val)


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (['1'], True),
        (['1', '2'], True),
        ([], True),
    ],
)
def test_integer_items(input_value, expected_output):
    rc = splint.SplintRC()
    assert rc.check_integer_items(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        (['a'], "Invalid value for"),
        (['1', 'a'], "Invalid value for"),
        (['a', '1'], "Invalid value for"),
    ],
)
def test_integer_ex_items(input_value, expected_output):
    rc = splint.SplintRC()
    with pytest.raises(SplintException):
        assert rc.check_integer_items(input_value) == expected_output


@pytest.mark.parametrize(
    "input_value, expected_output",
    [
        ([''], "Invalid value for"),
        (['', 'a'], "Invalid value for"),
        (['a', ''], "Invalid value for"),
    ],
)
def test_str_ex_items(input_value, expected_output):
    rc = splint.SplintRC()
    with pytest.raises(SplintException):
        assert rc.check_string_items(input_value) == expected_output


def test_json_exc():
    """Test exceptions raised while initializing SplintJsonRC with invalid input."""
    with pytest.raises(splint.SplintException):
        _ = splint_jsonrc.SplintJsonRC(cfg='./rc_files/test_bad.json', section='test1')

    with pytest.raises(splint.SplintException):
        _ = splint_jsonrc.SplintJsonRC(cfg='./rc_files/test_non_existant.json', section='foo')


def test_toml_exc():
    """Test exceptions raised while initializing SplintTomlRC with invalid input."""
    with pytest.raises(splint.SplintException):
        _ = splint_tomlrc.SplintTomlRC(cfg='./rc_files/test_non_existant.toml', section='foo')

    with pytest.raises(splint.SplintException):
        _ = splint_tomlrc.SplintTomlRC(cfg='./rc_files/test_bad.toml', section='test1')
