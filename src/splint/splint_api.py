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


@app.get("/splint/ruid/{ruid}")
async def check_ruid(ruid: str):
    """
    To call this function, use the following format:

    Using curl from a terminal:
    curl "http://<your_host>:<port>/splint/check/?ruid=first_ruid&ruid=second_ruid"

    Using Python requests library:
    import requests
    response = requests.get("http://<your_host>:<port>/splint/check/", params={"ruid": ["first_ruid", "second_ruid"]})
    print(response.json())
    """
    checker_ok()

    matched_funcs = [func for func in __splint_checker.collected if re.match(ruid, func.ruid)]
    if not matched_funcs:
        raise_404(msg=f"No function found with ruid {ruid}")


    results: List[splint.SplintResult] = []
    for func in matched_funcs:
        for result in func():
            results.append(result)

    return {'results': [result.as_dict() for result in results]}