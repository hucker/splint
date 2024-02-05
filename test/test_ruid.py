import logging
import sys

import pytest

from src import splint


@pytest.fixture(scope="function")
def sys_path():
    """
    Prevent sys.path from being modified by tests.

    This is a case where you should @pytest.mark.usefixtures("sys_path")
    at the top of each functionthat can modify sys.path. This will ensure
    that sys.path is reset after each test and prevent warnings
    about sys_path not being used.
    """
    original_sys_path = sys.path.copy()
    yield
    sys.path = original_sys_path


@pytest.mark.usefixtures("sys_path")
def test_ruid1():
    """Normal case all RUIDS are unique"""
    pkg = splint.SplintPackage(folder="./test/ruid", name="ruid")

    ruids = pkg.ruids()



    assert ruids == ["suid11", "suid12", "suid21", "suid22"]
    assert splint.valid_ruids(ruids)
    assert splint.ruid_issues(ruids) == "No issues found."


@pytest.mark.usefixtures("sys_path")
def test_ruid_dup():
    """Load up a package with duplicate RUIDS and blanks"""
    pkg = splint.SplintPackage(folder="./test/ruid_dup", name="ruid_dup")

    ruids = pkg.ruids()

    assert ruids == ["", "suid11", "suid12", "suid12", "suid21", "suid22", "suid22"]
    assert splint.valid_ruids(ruids) is False
    assert (
        splint.ruid_issues(ruids) == "Duplicates: suid12, suid22. Blank RUIDs present."
    )

@pytest.mark.usefixtures("sys_path")
def test_no_ruid():
    """Load a package that has no RUIDS"""
    pkg = splint.SplintPackage(folder="./test/ruid_empty", name="ruid_empty")

    ruids = pkg.ruids()


    # This package doesn't have RUIDS so all 4 should be empty
    assert ruids == ["", "", "", ""]

    # Now check
    assert splint.empty_ruids(ruids) is True
    assert splint.valid_ruids(ruids) is False
    assert splint.ruid_issues(ruids) == "RUIDS are not used."
