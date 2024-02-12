"""
Public API for the Splint project.
"""

from .splint_attribute import attributes  # noqa: F401
from .splint_attribute import get_attribute  # noqa: F401
from .splint_score import ScoreByFunctionBinary  # noqa: F401
from .splint_score import ScoreByFunctionMean  # noqa: F401
from .splint_score import ScoreByResult  # noqa: F401
from .splint_score import ScoreStrategy  # noqa: F401
from .splint_checker import SplintChecker  # noqa: F401
from .splint_checker import debug_progress  # noqa: F401
from .splint_checker import exclude_levels  # noqa: F401
from .splint_checker import exclude_phases  # noqa: F401
from .splint_checker import exclude_ruids  # noqa: F401
from .splint_checker import exclude_tags  # noqa: F401
from .splint_checker import keep_levels  # noqa: F401
from .splint_checker import keep_phases  # noqa: F401
from .splint_checker import keep_ruids  # noqa: F401
from .splint_checker import keep_tags  # noqa: F401
from .splint_checker import quiet_progress  # noqa: F401
from .splint_environment import SplintEnvFunction  # noqa: F401
from .splint_environment import SplintEnvironment  # noqa: F401
from .splint_environment import SplintEnvScope  # noqa: F401
from .splint_environment import make_constant_function  # noqa: F401
from .splint_exception import SplintException  # noqa: F401
from .splint_filter import and_filters  # noqa: F401
from .splint_filter import filter_level  # noqa: F401
from .splint_filter import filter_level_gt  # noqa: F401
from .splint_filter import filter_level_gte  # noqa: F401
from .splint_filter import filter_level_lt  # noqa: F401
from .splint_filter import filter_level_lte  # noqa: F401
from .splint_filter import filter_phase  # noqa: F401
from .splint_filter import filter_tag  # noqa: F401
from .splint_filter import keep_all  # noqa: F401
from .splint_filter import keep_level  # noqa: F401
from .splint_filter import keep_level_gt  # noqa: F401
from .splint_filter import keep_level_gte  # noqa: F401
from .splint_filter import keep_level_lt  # noqa: F401
from .splint_filter import keep_level_lte  # noqa: F401
from .splint_filter import keep_none  # noqa: F401
from .splint_filter import keep_phase  # noqa: F401
from .splint_filter import keep_tag  # noqa: F401
from .splint_filter import not_filter  # noqa: F401
from .splint_filter import or_filters  # noqa: F401
from .splint_function import SplintFunction  # noqa: F401
from .splint_module import SplintModule  # noqa: F401
from .splint_package import SplintPackage  # noqa: F401
from .splint_result import SplintResult  # noqa: F401
from .splint_result import overview  # noqa: F401
from .splint_ruid import empty_ruids  # noqa: F401
from .splint_ruid import module_ruids  # noqa: F401
from .splint_ruid import package_ruids  # noqa: F401
from .splint_ruid import ruid_issues  # noqa: F401
from .splint_ruid import valid_ruids  # noqa: F401

from .rule_files import rule_large_files  # noqa: F401
from .rule_files import rule_stale_files  # noqa: F401
from .rule_files import rule_path_exists  # noqa: F401
from .rule_files import rule_url_200 # noqa: F401

# Syntactic Sugar. Since this is used every time a result is returned it
# makes sense to make it easier to type.
SR = SplintResult

