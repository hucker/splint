import requests
from requests.exceptions import RequestException

from .splint_result import SplintResult as SR


def rule_url_200(urls, expected_status=200, timeout_sec=5):
    """Simple rule check to verify that URL is active."""

    for url in urls:
        try:
            response = requests.get(url, timeout=timeout_sec)

            if response.status_code == expected_status:
                yield SR(status=True, msg=f"URL {url} returned {response.status_code}")
            else:
                yield SR(
                    status=response.status_code == expected_status,
                    msg=f"URL {url} returned {response.status_code}",
                )

        except RequestException as ex:
            yield SR(status=False, msg=f"URL {url} exception.", except_=ex)



def is_mismatch(dict1, dict2):
    """
    Return the first differing values from dict1 and dict2
    Args:
        dict1:
        dict2:

    Returns: None if every key/value pair in dict1 is in dict, otherwise
            returns the first value that differs from dict 2

    """
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return False
    for key, value in dict1.items():
        if key not in dict2:
            return {key: value}
        if isinstance(value, dict):
            nested_result = is_mismatch(value, dict2[key])
            if nested_result is not None:  # Manual short-circuit the mismatch search.
                return {key: nested_result}
        elif value != dict2[key]:
            return {key: value}
    return None  # Return None if it is a subset.

def rule_web_api(url: str, json_d: dict, timeout_sec=5, expected_response=200):
    """Simple rule check to verify that URL is active."""
    response = requests.get(url, timeout=timeout_sec)

    if response.status_code != expected_response:
        yield SR(status=False, msg=f"URL {url} returned {response.status_code}")
        return

    # This handles an expected failure by return true but not checking the json
    if expected_response != 200:
        yield SR(status=True, msg=f"URL {url} returned {response.status_code}, no JSON comparison needed.")
        return

    response_json:dict = response.json()
    #d_status = verify_dicts(response_json, json_d)


    d_status = is_mismatch(json_d, response_json)

    if d_status is None:
        yield SR(status=True, msg=f"URL {url} returned the expected JSON {json_d}")
    else:
        yield SR(status=False, msg=f"URL {url} did not match at key {d_status}")
