import pathlib
import toml
from splint import SplintException
from splint import SplintRC
class SplintTomlRC(SplintRC):
    """
    Loads configurations from TOML files. Extends SplintRC.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        if not isinstance(section_data, dict):
            raise SplintException(f"Configuration section is not a dictionary in {cfg}")

        self.expand_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads and returns the requested section from a TOML file."""
        cfg = pathlib.Path(cfg)
        try:
            with cfg.open("rt", encoding="utf8") as t:
                config_data = toml.load(t)
        except (FileNotFoundError, toml.TomlDecodeError, AttributeError) as error:
            raise SplintException(f"TOML config file {cfg} error: {error}") from error

        return config_data.get(section, {})