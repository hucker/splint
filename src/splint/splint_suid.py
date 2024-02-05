"""
This module is used to check for SUID files in the system.
"""

from collections import Counter
from typing import List

from .splint_module import SplintModule
from .splint_package import SplintPackage
from .splint_function import SplintFunction


def module_suids(module: SplintModule) -> List[str]:
    """get a list of all the SUIDS in a module"""
    return [function.suid for function in module.functions]


def package_suids(package: SplintPackage) -> List[str]:
    """get a list of all the SUIDS in a package"""
    suids = []
    for module in package.modules:
        suids.extend(module_suids(module))
    return suids

def empty_suids(suids:List[str])->bool:
    """Check if all suids are empty"""
    return all((not suid for suid in suids))


def valid_suids(suids:List[str])->bool:
    """Check if all suids are valid"""
    return len(suids) == len(set(suids)) and "" not in suids


def suid_issues(suids:List[str])->str:
    """
    Provide a message about the issues with the SUIDs in the package.

    An issue is defined as either duplicate SUIDs (excluding blank entries)
    or the presence of blank SUIDs. The returned message will list any
    duplicate SUIDs and indicate whether blank SUIDs are present.

    If no issues are found, the returned message will indicate this.
    """
    suid_counts = Counter(suids)
    duplicates = [
        suid for suid, count in suid_counts.items() if count > 1 and suid != ""
    ]
    blanks = "" in suids

    issues = []
    if duplicates:
        issues.append(f"Duplicates: {', '.join(duplicates)}.")
    if blanks:
        if empty_suids(suids):
            issues.append("SUIDS are not used.")
        else:
            issues.append("Blank SUIDs present.")

    msg = " ".join(issues) if issues else "No issues found."
    return msg
