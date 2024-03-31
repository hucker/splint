from .splint_rc import SplintRC
from .splint_jsonrc import SplintJsonRC
from .splint_tomlrc import SplintTomlRC
from .splint_exception import SplintException


def splint_rc_factory(param: dict | str, section: str = "") -> SplintRC:
    """
    Factory function to create an instance of SplintRC or its subclasses.

    The type of RC instance is determined by the input `param`'s type and structure. This function
    enhances readability in higher-level code by abstracting the creation of different RC types.

    Parameters:
    param (dict|str): If a dict, it initializes SplintRC. If it's a string (a filename), we expect
                      it to determine the RC subclass type (SplintJsonRC or SplintTomlRC)
                      based on the file extension.
    section (str, optional): Provides additional context or a specific section. Defaults to "".

    Returns:
    SplintRC: An instance of SplintRC or its subclass based on the provided `param`.

    Raises:
    SplintException: If `param` isn't a dict or a string ending in ".json" or ".toml".
    """
    match param:
        case dict(d):
            if section == "":
                return SplintRC(rc_d=d)
            else:
                return SplintRC(rc_d=d[section])
        case str(s) if s.endswith('.toml'):
            return SplintTomlRC(cfg=s, section=section)
        case str(s) if s.endswith('.json'):
            return SplintJsonRC(cfg=s, section=section)
        case _:
            raise SplintException('Invalid parameter type for splint_rc_factory.')
