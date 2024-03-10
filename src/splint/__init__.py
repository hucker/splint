"""
Public API for the Splint project.
"""

from .rule_files import rule_large_files  # noqa: F401
from .rule_files import rule_max_files  # noqa: F401
from .rule_files import rule_path_exists  # noqa: F401
from .rule_files import rule_stale_files  # noqa: F401
from .rule_webapi import rule_url_200  # noqa: F401
from .rule_webapi import rule_web_api  # noqa: F401
from .splint_attribute import attributes  # noqa: F401
from .splint_attribute import get_attribute  # noqa: F401
# from .splint_attribute import _convert_to_minutes # noqa:F401
from .splint_checker import SplintChecker  # noqa: F401
from .splint_checker import SplintProgress # noqa: F401
from .splint_checker import SplintNoProgress # noqa; F401
from .splint_checker import SplintDebugProgress # noqa; F401
from .splint_checker import exclude_levels  # noqa: F401
from .splint_checker import exclude_phases  # noqa: F401
from .splint_checker import exclude_ruids  # noqa: F401
from .splint_checker import exclude_tags  # noqa: F401
from .splint_checker import keep_levels  # noqa: F401
from .splint_checker import keep_phases  # noqa: F401
from .splint_checker import keep_ruids  # noqa: F401
from .splint_checker import keep_tags  # noqa: F401
from .splint_exception import SplintException  # noqa: F401
from .splint_exception import SplintTypeError  # noqa: F401
from .splint_exception import SplintValueError  # noqa: F401
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
from .splint_score import ScoreBinaryFail  # noqa: F401
from .splint_score import ScoreBinaryPass  # noqa: F401
from .splint_score import ScoreByFunctionBinary  # noqa: F401
from .splint_score import ScoreByFunctionMean  # noqa: F401
from .splint_score import ScoreByResult  # noqa: F401
from .splint_score import ScoreStrategy  # noqa: F401
from .splint_immutable import SplintEnvList  # noqa: F401
from .splint_immutable import SplintEnvDict  # noqa: F401
from .splint_immutable import SplintEnvSet  # noqa: F401
from .splint_result import SplintYield # noqa: F401

# dataframe rules
try:
    import pandas as pd  # noqa: F401
    from .rule_dataframe import rule_validate_df_schema  # noqa: F401
    from .rule_dataframe import rule_validate_df_values_by_col  # noqa: F401
    from .splint_immutable import SplintEnvDataFrame  # noqa: F401
except ImportError:
    pass

# xlsx rules
try:
    import openpyxl
    from .rule_xlsx import rule_xlsx_a1_pass_fail
    from .rule_xlsx import rule_xlsx_df_pass_fail

except:
    pass

# Syntactic Sugar. Since this is used every time a result is returned it
# makes sense to make it easier to type.
SR = SplintResult
