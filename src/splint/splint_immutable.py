"""
Helper classes to support making environment variables with mutable values be less prone
to being changed by mistake.  We are under no presumption that we can stop people from
using a dynamic language.  These classes make the best effort to  prevent the user from
making edits to environment data that should be constant for the life of a rule
checking run.

THERE IS NO ASSURANCE THAT THIS WILL WORK IN ALL CASES. DON'T WRITE TO THE ENV VARIABLES!

"""
import pandas as pd

from .splint_exception import SplintException


class SplintEnvList(list):
    """
    Class representing a mutation-inhibited list. Mutational operations raise
    splint_exception.SplintException.

    Python being dynamic means forceful mutations can succeed. This class serves
    to prevent accidental changes by raising exceptions for mutating methods.

    Ideally, a copy is best to avoid mutation. But for large data sets, it's
    resource-demanding. ImmutableList protects large sets from unintended changes.
    """

    def __init__(self, *args):
        # super(SplintEnvList, self).__init__(*args)
        super().__init__(*args)

    def __setitem__(self, index, value):
        raise SplintException("Environment list does not support item assignment")

    def __delitem__(self, index):
        raise SplintException("Environment list doesn't support item deletion")

    def append(self, value):
        raise SplintException("Environment list is immutable, append is not supported")

    def extend(self, value):
        raise SplintException("Environment list is immutable, extend is not supported")

    def insert(self, index, value):
        raise SplintException("Environment list is immutable, insert is not supported")

    def remove(self, value):
        raise SplintException("Environment list is immutable, remove is not supported")

    def pop(self, index=-1):
        raise SplintException("Environment list is immutable, pop is not supported")

    def clear(self):
        raise SplintException("Environment list is immutable, clear is not supported")

    def sort(self, *args, **kwargs):
        raise SplintException("Environment list is immutable, sort is not supported")

    def reverse(self):
        raise SplintException("Environment list is immutable, reverse is not supported")


class SplintEnvDict(dict):
    """
    A class symbolizing a mutation-prohibited dictionary. Mutational operations raise
    a SplintException.

    Analogous to ImmutableList, Python's dynamic nature may allow forced mutations. This
    class prevents unintentional modifications to a dict object.
    """

    def __init__(self, *args, **kwargs):
        # super(SplintEnvDict, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        raise SplintException("Environment dict does not support item assignment")

    def __delitem__(self, key):
        raise SplintException("Environment dict doesn't support item deletion")

    def pop(self, k, d=None):
        raise SplintException("Environment dict is immutable, pop is not supported")

    def popitem(self):
        raise SplintException("Environment dict is immutable, popitem is not supported")

    def clear(self):
        raise SplintException("Environment dict is immutable, clear is not supported")

    def update(self, other=(), **kwargs):
        raise SplintException("Environment dict is immutable, update is not supported")

    def setdefault(self, key, default=None):
        raise SplintException("Environment dict is immutable, setdefault is not supported")


class SplintEnvDataFrame(pd.DataFrame):
    """
    A class for a non-mutable pandas DataFrame. Operations causing modifications raise a
    SplintException.

    Similar to ImmutableList and ImmutableDict, this class shields large dataframes from
    unintentional changes due to Python's dynamic nature.  This is not perfect and not
    intended to be perfect.  I'm just trying to help...
    """

    def __init__(self, *args, **kwargs):
        # super(SplintEnvDataFrame, self).__init__(*args, **kwargs)
        super().__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        raise SplintException("Environment DataFrame does not support item assignment")

    def __delitem__(self, key):
        raise SplintException("Environment DataFrame doesn't support column deletion")

    def append(self, other, ignore_index=False, verify_integrity=False, sort=None):
        raise SplintException("Environment DataFrame is immutable, append is not supported")

    def pop(self, item):
        raise SplintException("Environment DataFrame is immutable, pop is not supported")

    def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors='raise'):
        raise SplintException("Environment DataFrame is immutable, drop is not supported")

    def insert(self, loc, column, value, allow_duplicates=False):
        raise SplintException("Environment DataFrame is immutable, insert is not supported")


class SplintEnvSet(frozenset):
    """ Support immutable sets using frozenset """
