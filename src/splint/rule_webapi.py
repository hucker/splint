import requests
from requests.exceptions import RequestException
from requests.exceptions import Timeout
from .splint_result import SplintResult as SR

def rule_url_200(urls, timeout_sec=5):
    """Simple rule check to verify that URL is active."""
    for url in urls:
        try:
            response = requests.get(url, timeout=timeout_sec)

            if response.status_code == 200:
                yield SR(status=True, msg=f"URL {url} returned {response.status_code}")
            else:
                yield SR(
                    status=response.status_code == 200,
                    msg=f"URL {url} returned {response.status_code}",
                )

        except Timeout as e2:
            yield SR(status=False, msg=f"URL {url} exception {str(e2)}", except_=e2)

        except RequestException:
            yield SR(
                status=False, msg=f"URL {url} timed out after {timeout_sec} seconds"
            )


def _verify_dicts(d_check, d_truth, key_path=None):
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


def rule_web_api(url: str, json_d: dict, timeout_sec=5):
    """Simple rule check to verify that URL is active."""
    try:
        response = requests.get(url, timeout=timeout_sec)

        if response.status_code != 200:
            yield SR(status=False, msg=f"URL {url} returned {response.status_code}")
            return

        response_json = response.json()
        d_status = _verify_dicts(response_json, json_d)

        if d_status is None:
            yield SR(status=True, msg=f"URL {url} returned the expected JSON {json_d}")
        else:
            yield SR(status=False, msg=f"URL {url} did not match at key {d_status}")

    except Timeout as e2:
        yield SR(status=False, msg=f"URL {url} exception {str(e2)}", except_=e2)

    except RequestException:
        yield SR(status=False, msg=f"URL {url} timed out after {timeout_sec} seconds")
