import pytest
import splint
from splint import splint_rc


def test_base():

    rc = splint_rc.SplintRC(display_name="empty")
    assert rc.display_name == "empty"
    assert not rc.tags
    assert not rc.ruids
    assert not rc.phases
    assert not rc.ex_tags
    assert not rc.ex_ruids
    assert not rc.ex_phases

    rc = splint_rc.SplintRC(display_name="Ruids", ruids = ['ruid1', '-ruid2'])

    assert 'ruid1' in rc.ruids
    assert 'ruid2' in rc.ex_ruids
    assert not rc.ex_phases
    assert not rc.phases
    assert not rc.ex_tags
    assert not rc.tags

    rc = splint_rc.SplintRC(display_name="Phases",phases = ['phase1', '-phase2'])

    assert 'phase1' in rc.phases
    assert 'phase2' in rc.ex_phases
    assert not rc.ex_tags
    assert not rc.tags
    assert not rc.ex_ruids
    assert not rc.ruids

    rc = splint_rc.SplintRC(display_name="Tags",tags = ['tag1', '-tag2'])

    assert 'tag1' in rc.tags
    assert 'tag2' in rc.ex_tags
    assert not rc.ex_phases
    assert not rc.phases
    assert not rc.ex_ruids
    assert not rc.ruids

def test_everything():
    rc = splint_rc.SplintRC(display_name="FromList",
                            tags = ['tag1', '-tag2'],
                            phases = ['phase1', '-phase2'],
                            ruids = ['ruid1', '-ruid2'])
    assert 'tag1' in rc.tags
    assert 'tag2' in rc.ex_tags
    assert 'phase1' in  rc.phases
    assert 'phase2' in rc.ex_phases
    assert 'ruid1' in rc.ruids
    assert 'ruid2' in rc.ex_ruids

def test_everything_as_string():
    rc = splint_rc.SplintRC(display_name="FromString",
                            tags = 'tag1 -tag2',
                            phases = 'phase1 -phase2',
                            ruids = 'ruid1 -ruid2')
    assert 'tag1' in rc.tags
    assert 'tag2' in rc.ex_tags
    assert 'phase1' in  rc.phases
    assert 'phase2' in rc.ex_phases
    assert 'ruid1' in rc.ruids
    assert 'ruid2' in rc.ex_ruids

def test_everything_as_string():
    rc = splint_rc.SplintRC(display_name="FromString",
                            tags = 'tag1 -tag2 tag3',
                            phases = 'phase1 -phase2 phase3',
                            ruids = 'ruid1 -ruid2 ruid3')
    assert 'tag1' in rc.tags
    assert 'tag2' in rc.ex_tags
    assert 'tag3' in rc.tags
    assert 'phase1' in  rc.phases
    assert 'phase2' in rc.ex_phases
    assert 'phase3' in rc.phases
    assert 'ruid1' in rc.ruids
    assert 'ruid2' in rc.ex_ruids
    assert 'ruid3'in rc.ruids

@pytest.mark.parametrize("section", ['test1', 'test2'])
def test_toml(section):
    rc = splint_rc.SplintTomlRC(cfg='./rc_files/test.toml', section=section)
    assert 'ruid_foo' in rc.ruids
    assert 'ruid_bar' in rc.ruids
    assert 'ruid_baz' in rc.ex_ruids
    assert 'tag_spam' in rc.tags
    assert 'phase_alpha' in rc.phases
    assert 'phase_delta' in rc.ex_phases
@pytest.mark.parametrize("section", ['test1', 'test2'])
def test_json(section):
    rc = splint_rc.SplintJsonRC(cfg='./rc_files/test.json',section=section)
    assert 'ruid_foo' in rc.ruids
    assert 'ruid_bar' in rc.ruids
    assert 'ruid_baz' in rc.ex_ruids
    assert 'tag_spam' in rc.tags
    assert 'phase_alpha' in rc.phases
    assert 'phase_delta' in rc.ex_phases

def test_json_exc():

    with pytest.raises(splint.SplintException):
        _ = splint_rc.SplintJsonRC(cfg='./rc_files/test_bad.json', section='test1')

    with pytest.raises(splint.SplintException):
        _ = splint_rc.SplintJsonRC(cfg='./rc_files/test_non_existant.json', section='foo')


def test_toml_exc():
    with pytest.raises(splint.SplintException):
        _ = splint_rc.SplintTomlRC(cfg='./rc_files/test_non_existant.toml', section='foo')

    with pytest.raises(splint.SplintException):
        _ = splint_rc.SplintTomlRC(cfg='./rc_files/test_bad.toml', section='test1')
