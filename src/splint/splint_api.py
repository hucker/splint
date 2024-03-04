"""
This is a basic FastAPI wrapper around the splint library to provide access to a single splint
package.  This could be improved to handle multiple packages of checking functions.

It also doesn't have support for environment variables at this time.
"""

import re

from fastapi import FastAPI, HTTPException, Query
from starlette.responses import FileResponse

import splint.splint_checker

app = FastAPI()

# Globally define checker module
__splint_checker: splint.splint_checker.SplintChecker | None = None


def set_splint_checker(chk: splint.splint_checker.SplintChecker) -> None:
    """At this time we only handle one module at a time."""
    global __splint_checker

    __splint_checker = chk
    prepare_splint()


def prepare_splint():
    """Recalculate the initial conditions for splint"""
    __splint_checker.pre_collect()
    __splint_checker.prepare()


def checker_ok():
    """Verify that the splint object is initialized, this should always be the case"""

    # Look before you leap...not great python
    if __splint_checker is None:
        raise HTTPException(
            status_code=500,
            detail="SplintChecker is not set",
        )
    return True


def raise_400(msg: str):
    """Uniform 400 error message"""
    raise HTTPException(
        status_code=400,
        detail=msg
    )


@app.get("/splint/header")
async def get_result_header():
    """
    Return useful information about the collection of splint rule functions.

    """
    checker_ok()

    return __splint_checker.get_header()


def prep_rules():
    """Reload all the rules to makesure we are in a good state. """
    checker_ok()
    __splint_checker.pre_collect()
    __splint_checker.prepare()


def run_matched(matched_funcs, var) -> dict:
    """Given the list of function that matched some criteria that match, run only those."""

    # If there are no functions left then raise an exception (one could argue this should
    # just return the header with emtpy results).
    if not matched_funcs:
        raise_400(msg=f"No matched functions found for {var}")

    # WHen you run_all here the result is stored in the checker object.
    __splint_checker.collected = matched_funcs
    __splint_checker.run_all()

    return __splint_checker.as_dict()


@app.get("/splint/all")
async def check_all() -> dict:
    """Run the whole splint ruleset (careful with timeouts)"""
    checker_ok()

    __splint_checker.run_all()
    return __splint_checker.as_dict()


@app.get("/splint/rule_id_re/{rule_id}")
async def check_rule_id_regular_expression(rule_id: str):
    """
    Use this endpoint to check if any functions match the provided rule_id. The rule_id can be a regular expression.

    You can call this function using the following format:

    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/rule_id/<rule_id>"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/rule_id/{rule_id}")
    print(response.json())
    """
    prep_rules()
    matched_funcs = [func for func in __splint_checker.collected if re.match(rule_id, func.ruid)]
    return run_matched(matched_funcs, f"{rule_id=}")


@app.get("/splint/rule_ids/{rule_ids}")
async def check_rule_ids(rule_ids: str) -> dict:
    """
    Use this to check a comma or space separated list of rule_ids

    Note this is NOT a regular expression

    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/rule_id/<rule_id>"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/rule_id/{rule_id}")
    print(response.json())
    """
    prep_rules()
    rule_ids = [rule_id.strip() for rule_id in rule_ids.replace(",", " ").split()]
    matched_funcs = [func for func in __splint_checker.collected if func.ruid in rule_ids]
    return run_matched(matched_funcs, f"{rule_ids=}")


@app.get("/splint/tag/{tags}")
async def check_tags(tags: str) -> dict:
    """
    Tags is a comma-separated list of tags that is matched against tags for each rule.

    Here are some examples using a ',' or a ' ' as the separator.  It goes without saying that tags
    cannot have spaces in them.  They are not wordy descriptions, they are here for sorting.
    "tag1"
    "tag1,tag2,tag3"
    "tag1 tag2"

    You can call this function using the following format:

    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/tags/<tags>"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/tag/{tags}")
    print(response.json())
    """
    prep_rules()
    tags = [tag.strip() for tag in tags.replace(",", " ").split()]
    matched_funcs = [func for func in __splint_checker.collected if func.tag in tags]
    return run_matched(matched_funcs, f"{tags=}")


@app.get("/splint/level/")
async def check_level_range(
        low: int = Query(None, description="Level must be >= to this value."),
        high: int = Query(None, description="Level must be <= to this value.")) -> dict:
    """Checks if the levels of all marked functions are within an optional range.

    This function allows validating if the 'level' value of all the functions
    marked with a specific level is within an optionally passed range (low-high).
    The levels can be any integer values. If no range is provided,
    the function defaults to checking within the entire possible range.

    Args:
        low (int, optional): Lower boundary of the range. If provided, the level of the function must
            be greater than or equal to this value. Defaults to None.
        high (int, optional): Upper boundary of the range. If provided, the level of the function must
            be less than or equal to this value. Defaults to None.

    Returns:
        dict: A dictionary containing key 'results' with a list of results for each function that matches
        the level criteria. Each result is represented as a dictionary.

    Examples:
        Using curl from a terminal:
        curl http://localhost:8000/values/?low=10&high=20

        Using Python requests library:
        import requests
        response = requests.get(f"http://<your_host>:<port>/splint/check_level_range?low=10&high=20")
        print(response.json())
    """

    low, high = low or -1000000, high or 1000000
    prep_rules()
    matched_funcs = [func for func in __splint_checker.collected if low <= func.level <= high]
    return run_matched(matched_funcs, f"{low=} {high=}")


@app.get("/splint/phase/{phases}")
async def check_phase(phases: str) -> dict:
    """
    phases is a comma-separated list of tags that is matched against phase for each rule.

    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/level_lt/level"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/phases/{phases}")
    print(response.json())
    """
    prep_rules()
    phases = [phase.strip() for phase in phases.replace(" ", "").split(",")]
    matched_funcs = [func for func in __splint_checker.collected if func.phase in phases]
    return run_matched(matched_funcs, f"{phases=}")

@app.get("/apple-touch-icon-precomposed.png")
@app.get("/apple-touch-icon.png")
def get_apple_touch_icon():
    return FileResponse('apple_touch_icon.png')  # assumes you have an "images" directory your icon is located there