"""
Allow the usage of an XML file as an RC file.  Not sure why you want this.
"""
import pathlib
import xml.etree.ElementTree as ET
from splint import SplintException
from splint import SplintRC

class SplintXMLRC(SplintRC):
    """
    Loads configurations from XML files. Extends SplintRC.

    This class is VERY simple at this time and will work only for the most
    trivial XML files.  I'm happy to not need XML much anymore.
    """

    def __init__(self, cfg: str, section: str):
        package_data = self._load_config(cfg, section)

        # Convert the +/-attributes into separate inclusion/exclusion lists.
        self.expand_attributes(package_data)

    def _load_config(self, cfg: str, section: str) -> dict:
        """Loads tags, phases and ruids from a given package in the XML file."""
        cfg = pathlib.Path(cfg)
        try:
            tree = ET.parse(cfg)
            root = tree.getroot()

            package_data = {}
            for pkg in root.iter(section):
                for child in pkg:
                    package_data[child.tag] = [elem.text for elem in child.iter() if elem.text.strip()]

        except (FileNotFoundError, ET.ParseError, AttributeError) as error:
            raise SplintException(f"XML config file {cfg} error: {error}") from error

        return package_data
