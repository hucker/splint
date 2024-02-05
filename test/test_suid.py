
from src import splint
import logging
import sys

import pytest


@pytest.fixture(scope="function")
def sys_path():
    original_sys_path = sys.path.copy()
    yield
    sys.path = original_sys_path

def test_suid1(sys_path):
    pkg = splint.SplintPackage(folder="./test/suid", name="suid")

    suids = pkg.suids()

    logging.info(suids)

    assert suids == ['suid11', 'suid12', 'suid21', 'suid22']
    assert splint.valid_suids(suids)
    assert splint.suid_issues(suids) == "No issues found."



def test_suid_dup(sys_path):
    """Load up a package with duplicate SUIDS and blanks"""
    pkg = splint.SplintPackage(folder="./test/suid_dup", name="suid_dup")

    suids = pkg.suids()
    logging.info(suids)

    assert suids == ['','suid11', 'suid12', 'suid12', 'suid21', 'suid22', 'suid22']
    assert splint.valid_suids(suids) is False
    assert splint.suid_issues(suids) == "Duplicates: suid12, suid22. Blank SUIDs present."


def test_no_suid(sys_path):
    """Load a package that has no SUIDS"""
    pkg = splint.SplintPackage(folder="./test/suid_empty", name="suid_empty")

    suids = pkg.suids()

    logging.info(suids)

    # This package doesn't have SUIDS so all 4 should be empty
    assert suids == ['','','','']

    # Now check
    assert splint.empty_suids(suids) is True
    assert splint.valid_suids(suids) is False
    assert splint.suid_issues(suids) == "SUIDS are not used."
