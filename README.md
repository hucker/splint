#  Splint

A "linting" tool for anything that isn't code.

I have a collection of files, process, databases and log files.  I want to be able to press a button and have a tool tell me everyting is OK and given me clues about what isn't OK.

If you manage IT infrastucture, data pipelines or other systems that have dependencies spread around an organization `splint` can help, all you need to be able to do is write a little python.

## Overview

There are two pieces to splint, a set of rules (that look like `pytest` tests) and a runner.  The person responsible for the system
will generally write the rules while users of the system will be interested in the results of the checks.  For these users splint is like lint or ruff.  You run the ruleset against your system and look at the results.

For the person responsible for the rules, splint is like a toolset for writing a linter.  Not a code linter that aperates on CST/AST's of code.

Now those seem like tasks that don't need a bunch of infrastruture to support, but over time, 3 or 4 checks, turn into 10, and then 50 and then 100's and those checks are spread across many places that are difficult to track because many different tools have been patched together.  With splint there is a very low over head testing tool that can easily be connected to tools like typer, streamlit or FastAPI to run test quickly.

## Getting Started

Splint, works like `pytest`.  If you know pytest, you will be very good at `splint`. You write independent checks that can be run in any order to verify system state.  If you are used to writing tests with modules that start with "test" and functions that start with "test" it will be a breeze to get started. If you understand fixtures, that concept is also available through environments. Checks can be tagged with attributes so you can run various subsets of tests easily.  It is easy to write a trivial check with a single check function, but there is support for complete checking hierarchys.

A simple check module looks like this:

```python
from splint import splintResult,attributes
import pathlib

@attributes(tag="file")
def check_file_exists():
    """ Verify this that my_file exists """
    status = pathlib.Path("myfile.csv").exists()
    return splintResult(status=status,"Verify daily CSV file exists")

@attributes(tag="file")
def check_file_age():
    file = pathlib.Path("myfile.csv")
    modification_time = file.stat().st_mtime
    current_time = datetime.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    status = file_age_in_hours < 24.0
    if file_age_in_hours < 24:
        return SplintResult(status=True,"The file age is OK {file_age_in_hours}")
    else:
        return SplintResult(status=False,"The file is stale")
```

Throwing these two funtions in a file and pointing splint to this folder will automatically find the file and look in the file for the check functions and call them.  When comlete a collection of splint results is returned as a json file that you can
process in any way you want.  Put tham at an API end point for a FAST API app, point a streamlit dashboard at the folder or
have your own custom code hand

## WTH does splint derive from?

Splint is just a name that sounds cool.  When I started this I thought system-lint.  It has lint in the name

## Command Line Demo App For `splintit`:

Included is a light weight typer app that allows to point splint at a file, folder or repo (folder of folders) and run all tests via the command line.

To run it against a folder

`python -m splint_it.py -p path/to/package_folder``

A streamlit app is in work now.

```text
Usage: splint_it.py [OPTIONS]

 Run splint checks on a given target.


╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│            -m      TEXT  The module to run checks on. [default: None]             │
│            -p      TEXT  The package to run checks on. [default: None]            │
│            -r      TEXT  The repo to run checks on. [default: None]               │
│ --verbose  -v            Enable verbose output.                                   │
│ --help                   Show this message and exit.                              │
╰───────────────────────────────────────────────────────────────────────────────────╯
```
