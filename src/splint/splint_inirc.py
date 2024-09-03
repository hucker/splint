"""
Allow the usage of an INI file as an RC file.  
"""
import configparser

from .splint_exception import SplintException
from .splint_rc import SplintRC


class SplintIniRC(SplintRC):
    """
    Loads configurations from TOML files. Extends SplintRC.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads and returns the requested section from a TOML file."""
        try:
            config = configparser.ConfigParser()
            config.read(cfg, encoding="utf-8")
            if not section:
                raise SplintException("Section must be provided to read INI RC files.")
            d = {"tags": config.get(section, "tags"),
                 "ruids": config.get(section, "ruids"),
                 "phases": config.get(section, "phases")}

        except (FileNotFoundError, TypeError, configparser.Error, PermissionError) as error:
            raise SplintException(f"INI config file {cfg} error: {error}") from error

        return d
