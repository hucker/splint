import re
from typing import List

from fastapi import FastAPI, HTTPException
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


@app.get("/splint/all")
async def check_all():
    """Run the whole splint ruleset (careful with timeouts)"""
    checker_ok()

    __splint_checker.run_all()
    return __splint_checker.as_dict()


@app.get("/splint/rule_id/{rule_id}")
async def check_rule_id(rule_id: str):
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