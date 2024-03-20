"""
This set of classes is used to abastract a configuration file for splint.
The base class implements the configuration file as a dictionary while two subclasses allow the
creation aof config files based on TOML and json files.
"""
import json
import toml
import pathlib
from typing import List,Union,Tuple

from .splint_exception import SplintException


class SplintRC:
    """
    The SplintRC class which represents a set of Rule IDs (ruids), tags, and phases.
    Positive values are stored in ruids, tags, and phases.
    Negative values, which are indicated with a leading '-', are stored in the 'ex_' versions.
    A leading '+' is optional and ignored if present.

    It is assumed that higher level code will look at these lists and filter SplintFunctions
    accordingly.
    """

    def __init__(self, *, display_name: str = "NoName", ruids: List[str] = None, tags: List[str] = None,
                 phases: List[str] = None):
        self.display_name = display_name
        self.ruids, self.ex_ruids = self._split_items(ruids)
        self.tags, self.ex_tags = self._split_items(tags)
        self.phases, self.ex_phases = self._split_items(phases)

    def _load_config(self, cfg: str,section:str) -> dict: # pragma no cover
        raise NotImplementedError

    @staticmethod
    def _split_items(items: Union[List[str], str]) -> Tuple[List[str], List[str]]:
        """
        Transforms homogeneous or heterogeneous input 'items' into two separate lists.
        The processed input can either be a string of items separated by space or comma, or a list of items.
        The items are split into positive and negative items based on the leading '-' character.

        If the input is a string, it can contain elements prefixed with '+' or '-', denoting positive and negative items.
        Strings of items like "a -b +c d" would be transformed into lists like ['a', '-b', '+c', 'd'].

        The method returns two lists: one for positive items and another for items starting with '-' (negative).
        The '+' or '-' prefix is stripped in the resulting lists.

        Args:
            items (Union[List[str], str]): A string or list of items to be split. The string can contain
                                           items separated by spaces or commas.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing two lists. The first list contains positive items
                                         (those without a '-' prefix in the input). The second list
                                         contains negative items (those with a '-' prefix in the input).
        """
        if items is None:
            return [], []
        # split strings into a list if necessary
        if isinstance(items, str):
            items = items.replace(',', ' ').split()
        items_ = [item.lstrip('+') for item in items if not item.startswith('-')]
        ex_items = [item.lstrip('-') for item in items if item.startswith('-')]
        return items_, ex_items



class SplintJsonRC(SplintRC):
    """
    The SplintJsonRC class is a subclass of SplintRC that handles loading configuration from JSON files.

    Its main role is to manage and interact with JSON configuration files, parsing them into dictionaries suitable for use by the SplintRC superclass.

    This class overrides the __init__ method of the superclass and introduces a helper method _load_config that is specifically designed to load and return the requested section from the JSON file.

    Attributes:
        cfg (str): Path of the configuration file.
        section (str): Specific section within the JSON to focus on.

    Usage:
        cfg = "path/to/json/file.json"
        section = "desired_section"
        splint_json_instance = SplintJsonRC(cfg, section)
    """
    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        if not isinstance(section_data, dict):
            raise SplintException(f"Configuration section is not a dictionary in {cfg}")

        super().__init__(display_name=section_data.get('display_name','NoName'),
                         ruids=section_data.get('ruids',[]),
                         tags=section_data.get('tags',[]),
                         phases=section_data.get('phases',[]))

    def _load_config(self, cfg: str, section: str) -> dict:
        cfg = pathlib.Path(cfg)
        try:
            with cfg.open("rt", encoding="utf8") as j:
                config_data = json.load(j)
        except (FileNotFoundError, json.JSONDecodeError,AttributeError) as error:
            raise SplintException(f"Configuration file {cfg} not found: {error}")from error

        return config_data.get(section, {})


class SplintTomlRC(SplintRC):
    """
    The SplintRCToml class represents a set of RuleIDs (ruids), tags, and phases based on a TOML file.
    This class extends the SplintRC class, overriding its __init__ method to populate ruids,
    tags, and phases from a given TOML file.

    Upon initialization, the class attempts to open and read the specified TOML file. Any issues
    with file opening or TOML decoding result in a SplintException.

    Finally, the class calls the parent class __init__ to initialize the ruids, tags,
    and phases using the data in the TOML file.

    Usage:
    --------
    cfg = "path/to/toml/file.toml"
    section = "some_section"
    splint_rc_toml_instance = SplintRCToml(cfg, section)
    """
    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        if not isinstance(section_data, dict):
            raise SplintException(f"Configuration section is not a dictionary in {cfg}")

        super().__init__(display_name=section_data.get('display_name','NoName'),
                         ruids=section_data.get('ruids',[]),
                         tags=section_data.get('tags',[]),
                         phases=section_data.get('phases',[]))

    def _load_config(self, cfg: str, section: str) -> dict:
        cfg = pathlib.Path(cfg)
        try:
            with cfg.open("rt", encoding="utf8") as t:
                config_data = toml.load(t)
        except (FileNotFoundError, toml.TomlDecodeError,AttributeError) as error:
            raise SplintException(f"Configuration file {cfg} error: {error}") from error

        return config_data.get(section, {})