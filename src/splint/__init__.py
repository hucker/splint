"""
Public API for the Splint project.
"""

from .splint_attribute import (
    attributes,  # noqa: F401
    get_attribute,  # noqa: F401
)
from .splint_environment import (
    SplintEnvFunction,  # noqa: F401
    SplintEnvironment,  # noqa: F401
    SplintEnvScope,  # noqa: F401
    make_constant_function,  # noqa: F401
)
from .splint_exception import SplintException  # noqa: F401
from .splint_filter import (
    and_filters,  # noqa: F401
    filter_level,  # noqa: F401
    filter_level_gt,  # noqa: F401
    filter_level_gte,  # noqa: F401
    filter_level_lt,  # noqa: F401
    filter_level_lte,  # noqa: F401
    filter_phase,  # noqa: F401
    filter_tag,  # noqa: F401
    keep_all,  # noqa: F401
    keep_level,  # noqa: F401
    keep_level_gt,  # noqa: F401
    keep_level_gte,  # noqa: F401
    keep_level_lt,  # noqa: F401
    keep_level_lte,  # noqa: F401
    keep_none,  # noqa: F401
    keep_phase,  # noqa: F401
    keep_tag,  # noqa: F401
    not_filter,  # noqa: F401
    or_filters,  # noqa: F401
)
from .splint_function import SplintFunction  # noqa: F401
from .splint_module import SplintModule  # noqa: F401
from .splint_package import SplintPackage  # noqa: F401
from .splint_result import (
    SplintResult,  # noqa: F401
    overview,  # noqa: F401
)
from .splint_ruid import (
    empty_ruids,  # noqa: F401
    module_ruids,  # noqa: F401
    package_ruids,  # noqa: F401
    ruid_issues,  # noqa: F401
    valid_ruids,  # noqa: F401
)

from .splint_checker import (
    exclude_levels,  # noqa: F401
    exclude_phases,  # noqa: F401
    exclude_ruids,  # noqa: F401
    exclude_tags,  # noqa: F401
    keep_levels,  # noqa: F401
    keep_phases,  # noqa: F401
    keep_ruids,  # noqa: F401
    keep_tags,  # noqa: F401
    SplintChecker,  # noqa: F401
)

# Syntactic Sugar. Since this is used every time a result is returned it
# makes sense to make it easier to type.
SR = SplintResult
