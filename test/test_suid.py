
from src import splint


def test_suid1():
    pkg = splint.SplintPackage(folder="./test/suid", name="Suid")

    suids = pkg.suids()

    assert suids == ['suid11', 'suid12', 'suid21', 'suid22']
    assert splint.valid_suids(suids)
    assert splint.suid_issues(suids) == "No issues found"


def test_suid_dup():
    """Load up a package with duplicate SUIDS and blanks"""
    pkg = splint.SplintPackage(folder="./test/suid_dup", name="Suid")

    suids = pkg.suids()

    assert suids == ['','suid11', 'suid12', 'suid12', 'suid21', 'suid22', 'suid22']
    assert splint.valid_suids(suids) is False
    assert splint.suid_issues(suids) == "Duplicates: suid12, suid22. Blank SUIDs present."



def test_no_suid():
    """Load a package that has no SUIDS"""
    pkg = splint.SplintPackage(folder="./test/suid_empty", name="Suid")

    suids = pkg.suids()

    # This package doesn't have SUIDS so all 4 should be empty
    assert suids == ['','','','']

    # Now check
    assert splint.empty_suids(suids) is True
    assert splint.valid_suids(suids) is False
    assert splint.suid_issues(suids) == "SUIDS are not used."