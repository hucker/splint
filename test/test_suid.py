import logging
import sys

import pytest

from src import splint


@pytest.fixture(scope="function")
def sys_path():
    original_sys_path = sys.path.copy()
    yield
    sys.path = original_sys_path


def test_ruid1(sys_path):
    pkg = splint.SplintPackage(folder="./test/ruid", name="ruid")

    ruids = pkg.ruids()


    assert ruids == ["suid11", "suid12", "suid21", "suid22"]
    assert splint.valid_ruids(ruids)
    assert splint.ruid_issues(ruids) == "No issues found."


def test_ruid_dup(sys_path):
    """Load up a package with duplicate RUIDS and blanks"""
    pkg = splint.SplintPackage(folder="./test/ruid_dup", name="ruid_dup")

    ruids = pkg.ruids()

    assert ruids == ["", "suid11", "suid12", "suid12", "suid21", "suid22", "suid22"]
    assert splint.valid_ruids(ruids) is False
    assert (
        splint.ruid_issues(ruids) == "Duplicates: suid12, suid22. Blank RUIDs present."
    )


def test_no_ruid(sys_path):
    """Load a package that has no RUIDS"""
    pkg = splint.SplintPackage(folder="./test/ruid_empty", name="ruid_empty")

    ruids = pkg.ruids()


    # This package doesn't have RUIDS so all 4 should be empty
    assert ruids == ["", "", "", ""]

    # Now check
    assert splint.empty_ruids(ruids) is True
    assert splint.valid_ruids(ruids) is False
    assert splint.ruid_issues(ruids) == "RUIDS are not used."
