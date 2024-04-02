"""
This module makes dealing with configuration files a bit easier as it supports JSON and TOML
out of the box.

I also have begun using the patch statement and this was a reasonable place to use it soe
I have provided two implementations.
"""

import sys
from .splint_rc import SplintRC
from .splint_jsonrc import SplintJsonRC
from .splint_tomlrc import SplintTomlRC
from .splint_xmlrc import SplintXMLRC
from .splint_exception import SplintException
from .splint_inirc import SplintIniRC

if sys.version_info[:2] >= (3, 10):
    def splint_rc_factory(param: dict | str, section: str = "") -> SplintRC:
        """
        Factory function to create an instance of SplintRC or its subclasses for Python 3.10 and above.
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
            case str(s) if s.endswith('.xml'):
                return SplintXMLRC(cfg=s, section=section)
            case str(s) if s.endswith('.ini'):
                return SplintIniRC(cfg=s, section=section)
            case _:
                raise SplintException('Invalid parameter type for splint_rc_factory.')
else: # pragma: no cover
    def splint_rc_factory(param, section: str = "") -> SplintRC:
        """
        Factory function to create an instance of SplintRC or its subclasses for Python below 3.10.
        """
        if isinstance(param, dict):
            if not section:
                return SplintRC(rc_d=param)
            else:
                return SplintRC(rc_d=param[section])
        elif isinstance(param, str):
            if param.endswith('.toml'):
                return SplintTomlRC(cfg=param, section=section)
            elif param.endswith('.json'):
                return SplintJsonRC(cfg=param, section=section)
            elif param.endswith('.xml'):
                return SplintXMLRC(cfg=param, section=section)
            elif param.endswith('.ini'):
                return SplintIniRC(cfg=param, section=section)

        raise SplintException(f'Invalid parameter type for splint_rc_factory {param=}-{section=}.')