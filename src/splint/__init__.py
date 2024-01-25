"""
Public API for the Splint project.
"""


from .splint_environment import SplintEnvironment  # noqa: F401
from .splint_package import SplintPackage          # noqa: F401
from .splint_result import SplintResult            # noqa: F401
from .splint_exception import SplintException      # noqa: F401
from .splint_module import SplintModule            # noqa: F401
from .splint_function import SplintFunction        # noqa: F401
from .splint_repo import SplintRepo                # noqa: F401
from .splint_filter import filter_level             # noqa: F401
from .splint_filter import filter_tag               # noqa: F401
from .splint_filter import filter_phase             # noqa: F401
from .splint_filter import keep_level              # noqa: F401
from .splint_filter import keep_tag                # noqa: F401
from .splint_filter import keep_phase              # noqa: F401
from .splint_filter import and_filters              # noqa: F401
from .splint_filter import or_filters               # noqa: F401
from .splint_filter import keep_level_gt           # noqa: F401
from .splint_filter import keep_level_gte          # noqa: F401
from .splint_filter import keep_level_lt           # noqa: F401
from .splint_filter import keep_level_lte          # noqa: F401
from .splint_filter import filter_level_gt          # noqa: F401
from .splint_filter import filter_level_gte         # noqa: F401
from .splint_filter import filter_level_lt          # noqa: F401
from .splint_filter import filter_level_lte         # noqa: F401
from .splint_filter import not_filter               # noqa: F401
from .splint_filter import keep_none               # noqa: F401
from .splint_filter import keep_all                # noqa: F401
from .splint_attribute import get_attribute            # noqa: F401
from .splint_attribute import attributes           # noqa: F401
from .splint_result import overview                # noqa: F401

# Syntactic Sugar. Since this is used every time a result is returned it
# makes sense to make it easier to type.
SR = SplintResult
