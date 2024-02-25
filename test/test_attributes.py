import pytest

import splint
import src.splint.splint_attribute as splint_attribute


def test_attr_ttl():
    tests = [
        ["0", ["m", "minute", "min"], 0],
        ["0", ["s", "sec", "second","seconds"], 0],
        ["0", ["h", "hr", "hour"], 0],
        ["1", [""], 1.0],
        ["10.5", [""], 10.5],
        ["0.25", [""], 0.25],
        ["0.5", ["h", "hr", "hour"], 30],
        ["1", ["h", "hr", "hour","hours"], 60],
        ["2", ["h", "hr", "hour"], 120],
        ["30", ["s", "sec", "second"], .5],
        ["60", ["s", "sec", "second"], 1],
        ["630", ["s", "sec", "second"], 10.5],
        ["1", ["m", "minute", "min"], 1],
        [".5", ["m", "minute", "min"], 0.5],
        ["10", ["m", "minute", "min"], 10],
        ["101.5", ["m", "minute", "min","minutes"], 101.5],

    ]
    seps = ['', ' ', '\t', '   ']

    for ttl, units, result in tests:
        for unit in units:
            for sep in seps:
                # no space '1hr' case
                assert splint_attribute._parse_ttl_string(f'{ttl}{sep}{unit}') == result


def test_ttl_fail():
    units = [
        ["m", "minute", "min","minutes"],
        ["s", "sec", "second","seconds"],
        ["h", "hr", "hour",'hrs'],
        [""]
    ]
    bad_times = ["-0.1", "-1", "-1.0", "-1."]
    seps = ['', ' ', '\t', '   ']
    for unit_group in units:
        for unit in unit_group:
            for bad_time in bad_times:
                for sep in seps:
                    with pytest.raises(splint.SplintException):
                        s = f"{bad_time}{sep}{unit}"
                        splint_attribute._parse_ttl_string(s)

