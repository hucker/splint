"""
Helper classes to support making environment variables with mutable values be less prone
to being changed by mistake.  We are under non presumption that we can stop people from
using a dynamic language.  These classes make a best effort to  prevent the user from
making edits to environment data that should be constant for the life of a rule
checking run.

THERE IS NO ASSURANCE THAT THIS WILL WORK IN ALL CASES. DON'T WRITE TO THE ENV VARIABLES!

"""
import pandas as pd
from .splint_exception import SplintException




class SplintEnvList(list):
    """
    A class that represents a list where mutation is not permitted. Operations that would normally
    modify the list instead raise a SplintException.

    Python being a dynamic language means that determined attempts to mutate the list could still succeed.
    However, this class serves to prevent inadvertent modifications by making mutating methods explicitly raise exceptions.

    While the ideal situation would be to make a copy, for larger data sets this may not be feasible due to resource
    constraints. As such, the ImmutableList serves as a safeguard to protect large data sets from unintended modifications.
    """
    def __init__(self, *args):
        super(SplintEnvList, self).__init__(*args)

    def __setitem__(self, index, value):
        raise SplintException("Environment list does not support item assignment")

    def __delitem__(self, index):
        raise SplintException("Environment list doesn't support item deletion")

    def append(self, value):
        raise SplintException("Environment list is immutable, append operation is not supported")

    def extend(self, value):
        raise SplintException("Environment list is immutable, extend operation is not supported")

    def insert(self, index, value):
        raise SplintException("Environment list is immutable, insert operation is not supported")

    def remove(self, value):
        raise SplintException("Environment list is immutable, remove operation is not supported")

    def pop(self, index=-1):
        raise SplintException("Environment list is immutable, pop operation is not supported")

    def clear(self):
        raise SplintException("Environment list is immutable, clear operation is not supported")

    def sort(self, *args, **kwargs):
        raise SplintException("Environment list is immutable, sort operation is not supported")

    def reverse(self):
        raise SplintException("Environment list is immutable, reverse operation is not supported")

class SplintEnvDict(dict):
    """
        A class that represents a dictionary where mutation is not permitted. Operations that would normally
        modify the dictionary instead raise a SplintException.

        Similar to ImmutableList, while Python's dynamic nature could allow mutation through determined attempts,
        this class serves to prevent inadvertent modifications to a dict object.
        """
    def __init__(self, *args, **kwargs):
        super(SplintEnvDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        raise SplintException("Environment dict does not support item assignment")

    def __delitem__(self, key):
        raise SplintException("Environment dict doesn't support item deletion")

    def pop(self, k, d=None):
        raise SplintException("Environment dict is immutable, pop operation is not supported")

    def popitem(self):
        raise SplintException("Environment dict is immutable, popitem operation is not supported")

    def clear(self):
        raise SplintException("Environment dict is immutable, clear operation is not supported")

    def update(self, other=(), **kwargs):
        raise SplintException("Environment dict is immutable, update operation is not supported")

    def setdefault(self, key, default=None):
        raise SplintException("Environment dict is immutable, setdefault operation is not supported")

class SplintEnvDataFrame(pd.DataFrame):
    """
    A class that represents a DataFrame from pandas where mutation is not permitted. Operations that would normally
    modify the DataFrame instead raise a SplintException.

    Like the ImmutableList and ImmutableDict classes, this class aims to protect large dataframes from unintended
    modifications due to Python's dynamic nature.
    """

    def __init__(self, *args, **kwargs):
        super(SplintEnvDataFrame, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        raise SplintException("Environment DataFrame does not support item assignment")

    def __delitem__(self, key):
        raise SplintException("Environment DataFrame doesn't support column deletion")

    def append(self, other, ignore_index=False, verify_integrity=False, sort=None):
        raise SplintException("Environment DataFrame is immutable, append operation is not supported")

    def pop(self, item):
        raise SplintException("Environment DataFrame is immutable, pop operation is not supported")

    def drop(self, labels=None, axis=0, index=None, columns=None, level=None, inplace=False, errors='raise'):
        raise SplintException("Environment DataFrame is immutable, drop operation is not supported")

    def insert(self, loc, column, value, allow_duplicates=False):
        raise SplintException("Environment DataFrame is immutable, insert operation is not supported")


class SplintEnvSet(frozenset):
    """ Support immutable sets using frozenset """
    pass
