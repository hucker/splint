import re
from typing import List

from fastapi import FastAPI, HTTPException, Query
import splint.splint_checker

app = FastAPI()

# Globally define checker module
__splint_checker:splint.splint_checker.SplintChecker = None


def set_splint_checker(chk: splint.splint_checker.SplintChecker) -> None:
    global __splint_checker
    __splint_checker = chk


def checker_ok():
    if __splint_checker is None:
        raise HTTPException(
            status_code=500,
            detail="SplintChecker is not set",
        )
    return True


def raise_404(msg: str):
    raise HTTPException(
        status_code=404,
        detail=msg
    )

@app.get("/splint/header")
async def get_result_header():
    """
    Return useful information about the collection of splint rule functions.

    """
    checker_ok()

    return __splint_checker.get_header()

@app.get("/splint/all")
async def check_all():
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
    checker_ok()

    matched_funcs = [func for func in __splint_checker.collected if re.match(rule_id, func.ruid)]
    if not matched_funcs:
        raise_404(msg=f"No function found with ruid {rule_id}")

    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}

@app.get("/splint/rule_ids/{rule_ids}")
async def check_rule_ids(rule_ids: str):
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
    checker_ok()
    rule_ids = [rule_id.strip() for rule_id in rule_ids.replace(",",' ').split()]
    matched_funcs = [func for func in __splint_checker.collected if func.ruid in rule_ids]
    if not matched_funcs:
        raise_404(msg=f"No function found with in {rule_ids}")

    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}


@app.get("/splint/tag/{tags}")
async def check_tags(tags: str):
    """
    Tags is a comma-separated list of tags that is matched against tags for each rule.

    Here are some examples using a , or a ' ' as the separator.  It goes without saying that tags
    cannot have spaces in them.  They are not wordy descriptions, they are here for soerting.
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
    checker_ok()

    tags = [tag.strip() for tag in tags.replace(","," ").split()]

    matched_funcs = [func for func in __splint_checker.collected if func.tag in tags]

    if not matched_funcs:
        raise_404(msg=f"No function found with matching {tags}")

    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}


@app.get("/splint/level_gt/level}")
async def check_level_greater(level: int):
    """
    Check for all functions marked with level greater than level.


    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/level_gt/level"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/level_gt/{level}")
    print(response.json())
    """
    checker_ok()


    matched_funcs = [func for func in __splint_checker.collected if func.level > level]

    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}


@app.get("/splint/level_lt/level}")
async def check_level_less(level: int):
    """
    Check for all functions marked with level less that level.


    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/level_lt/level"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/level_lt/{level}")
    print(response.json())
    """
    checker_ok()

    matched_funcs = [func for func in __splint_checker.collected if func.level < level]

    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}




@app.get("/splint/phase/{phases}")
async def check_phase(phases: str):
    """
    pahses is a comma-separated list of tags that is matched against phase for each rule.

    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/level_lt/level"

    Using Python requests library:
    import requests
    response = requests.get(f"http://<your_host>:<port>/splint/level_lt/{level}")
    print(response.json())
    """
    checker_ok()

    phases = [phase.strip() for phase in phases.replace(" ", "").split(",")]

    matched_funcs = [func for func in __splint_checker.collected if func.phase in phases]

    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}