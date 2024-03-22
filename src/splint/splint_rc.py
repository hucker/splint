"""
Handles configuration abstraction for splint, includes classes to parse TOML and JSON.
"""
from collections import Counter
from typing import List, Tuple, Union

import toml

from .splint_exception import SplintException


class SplintRC:
    """
    Represents a set of Rule IDs, tags, and phases. Handles positive and negative values.
    """

    def __init__(self, *,
                  display_name: str = "NoName",
                  ruids: str | List[str] = None,
                  tags: str | List[str] = None,
                  phases: str | List[str] = None,
                  levels: str | List[int] = None,):

        self.set_attributes({
            'display_name': display_name,
            'ruids': ruids,
            'tags': tags,
            'phases': phases,
            'levels': levels,
        })

    def _load_config(self, cfg: str, section: str) -> dict:  # pragma no cover
        raise NotImplementedError

    def set_attributes(self, data: dict,name:str="NoName"):
        """
        Sets SplintRC attributes from a data dictionary.
        """
        self.display_name = data.get('display_name', name)
        self.ruids, self.ex_ruids = self._split_items(data.get('ruids', []))
        self.tags, self.ex_tags = self._split_items(data.get('tags', []))
        self.phases, self.ex_phases = self._split_items(data.get('phases', []))
        self.levels, self.ex_levels = self._split_items(data.get('levels', []))

        # Define a dictionary that maps attributes to their validation functions
        attribute_validations = {
            "ruids": self.check_string_items,
            "tags": self.check_string_items,
            "phases": self.check_string_items,
            "levels": self.check_integer_items,
        }

        self.validate_attributes(attribute_validations)

    def validate_attributes(self, attributes):
        """
        Applies validation functions on provided attributes.
        """
        for attribute, validation_func in attributes.items():
            validation_func(getattr(self, attribute))
            validation_func(getattr(self, "ex_" + attribute))

    @staticmethod
    def _split_items(items: Union[List[str], str]) -> Tuple[List[str], List[str]]:
        """
        Splits items into positive and negative lists. Supports comma or space-separated strings.
        """
        if not items:
            return [], []
        # split strings into a list if necessary
        if isinstance(items, str):
            items = items.replace(',', ' ').split()

        # There are multiple str's going on here that might look odd.  It is possible
        # that we got integers or floats which are valid.  This makes them into strings,
        # so we can do the +/- checking stuff
        pos_items = [str(item).lstrip('+') for item in items if not str(item).startswith('-')]
        neg_items = [str(item).lstrip('-') for item in items if str(item).startswith('-')]

        if (dups := [item for item, count in Counter(items).items() if count > 1]):
            raise SplintException(f"Duplicate attributes - {dups}")

        if (intersect := set(items) & set(neg_items)):
            raise SplintException(f"Attributes in list and exclusion list = {intersect}")

        return pos_items, neg_items

    @staticmethod
    def check_string_items(items: List[str]) -> bool:
        """Validates that all items are non-empty strings."""
        for item in items:
            if item == '':
                raise SplintException(f"Invalid string value: '{item}'. Strings should not be empty.")
        return True

    @staticmethod
    def check_integer_items(items: List[str]) -> bool:
        """Validates that all items can be casted to integers."""
        for item in items:
            if not item.isdigit():
                raise SplintException(f"Invalid value for level: '{item}'. Levels should be integers.")
        return True


