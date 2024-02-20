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


def _verify_dicts(d_check, d_truth, key_path=None):
    """Recursive dictionary verifier"""
    if key_path is None:
        key_path = []
    for key, value in d_truth.items():
        if key not in d_check:
            return key_path + [key]
        if isinstance(value, dict):
            # If the value is a dict, call the function recursively
            failed_key_path = _verify_dicts(d_truth[key], value, key_path + [key])
            if failed_key_path is not None:
                return failed_key_path
        else:
            if d_check[key] != value:
                return key_path + [key]
    return None


def rule_web_api(url: str, json_d: dict, timeout_sec=5, expected_response=200):
    """Simple rule check to verify that URL is active."""
    try:
        response = requests.get(url, timeout=timeout_sec)

        if response.status_code != expected_response:
            yield SR(status=False, msg=f"URL {url} returned {response.status_code}")
            return

        # This handles an expected failure by return true but not checking the json
        if expected_response != 200:
            yield SR(status=True, msg=f"URL {url} returned {response.status_code}, no JSON comparison needed.")
            return

        response_json = response.json()
        d_status = _verify_dicts(response_json, json_d)

        if d_status is None:
            yield SR(status=True, msg=f"URL {url} returned the expected JSON {json_d}")
        else:
            yield SR(status=False, msg=f"URL {url} did not match at key {d_status}")

    except RequestException as ex:
        yield SR(status=False, msg=f"URL {url} had exception {ex}", except_=ex)
