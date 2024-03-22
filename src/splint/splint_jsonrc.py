import json
import pathlib
from splint import SplintException
from splint import SplintRC

class SplintJsonRC(SplintRC):
    """
    Loads configurations from JSON files. Extends SplintRC.
    """

    def __init__(self, cfg: str, section: str):
        section_data = self._load_config(cfg, section)

        if not isinstance(section_data, dict):
            raise SplintException(f"Configuration {section=} is not a dictionary in {cfg}")

        self.set_attributes(section_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads and returns the requested section from a JSON file."""
        cfg = pathlib.Path(cfg)
        try:
            with cfg.open("rt", encoding="utf8") as j:
                config_data = json.load(j)
        except (FileNotFoundError, json.JSONDecodeError, AttributeError) as error:
            raise SplintException(f"JSON config {cfg} error: {error}") from error

        return config_data.get(section, {})


