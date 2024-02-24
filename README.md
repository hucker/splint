# Splint

Splint lets you create a lint like tool for anything you can write rules for using a declarative style similar to 
`pytest`.  It takes just a few lines of simple code to write tests that can be made available via `FastAPI` or 
`streamlit`.

## Overview 
Splint is a linting tool designed for tasks beyond traditional code analysis. Inspired by the effectiveness of `pylint`
in identifying and rectifying issues in code,
I envisioned a tool that could extend this functionality to various aspects of my workflows with just a button press. I
wanted something that would allow me to "lint" anything.
I also want to trivially have access to the test results for use with Streamlit and FastAPI.

After experimenting with different approaches involving scripting and configuration files and code that was usually a
long list of verifications,
I concluded that a `pytest`-like framework could be the solution. While `pytest` served a different purpose, I
appreciated its declarative style for writing
independent tests, which are then managed by the framework. This led to the creation of Splint, a tool that allows you
to run a set of rules against a system
and get detailed results and a simple "score" for the run. If all tests pass you get 100% and a long list of passes. 

If you there are failures you get detailed information about what failed as well as a score < 100%.

`Splint` generalizes this pattern.

If you're familiar with `pytest`, adapting to `splint` will be fairly obvious. Both follow a similar structure. `Splint`
defines rules in files, where rules are python functions that plugin to your application with very little effort. 
There is almost no boilerplate and almost everything is automatically detected. All you need to do is write simple
(and at times not-simple) python code that checks your rules.

Splint's autoloaded modules and rule functions support parameters, mirroring some of the behavior of `pytest`. These
parameters are dynamically built from the environment, following a hierarchy of your system. While it may sound 
intricate, if you grasp `pytest`, you'll easily understand Splint.

The ideas in `splint` have worked very well in environments where the end users are NOT programmers, coders or people
who consider themselves part a development team. The benefit from `splint` is a tool telling you what is what items
need to be corrected to make your system pass.  It does so by checking the outputs you've aggreed to created for
your process.  Ideally these outputs are just the normal output of your daily work flow, rather than abiding by a
rigid system. If you all agree on the ruleset, people will work in peace driving he error count to 0.

## Why not pytest?

Good question.  `Pytest` is big and complicated while `splint` is small and less complicated. `Pytest` is for code and 
the ways that code can break, it is tied intricately to `python`. If you have a huge set of rules and have a team 
managing them, `pytest` might be your answer, but probably not.  It solves a similar but different problem.

## Getting Started

As I said, `splint`, works like `pytest`. If you know `pytest`, you will be good at `splint`. You write independent rules
that can be run in any order to verify system state. They should be atomic. If you are used to writing tests with modules 
that start with "test" and functions that start with "test" it will be a breeze to get started. If you understand 
fixtures, that concept is also available through environments. Rules are tagged with attributes, so you can run 
various subsets of tests easily. 

From the most simple you could write rules like this...not even a reference to splint.

```python
def check_boolean():
    return get_drive_space('/foo') > 1_000_000_000


def check_yielded_values():
    yield get_drive_space('/foo') > 1_000_000_000)
    yield get_drive_space('/fum') > 1_000_000_000)
```

As you might expect running this will provide 3 passing test results.

You can up your game and return status message info:
From the most simple you could write rules like this:

```python
from splint import SplintResult, SR


def check_boolean():
    return SplintResult(status=get_drive_space('/foo') > 1_000_000_000, msg="Drive space check for foo")


def check_yielded_values():
    yield SR(status=get_drive_space('/foo') > 1_000_000_000, msg="Drive space check for foo")
    yield SR(status=get_drive_space('/fum') > 1_000_000_000, msg="Drive space check for fum")
```

As you might expect running this will also provide 3 passing test results.

Now we can add more complexity. Tag a test functions with attributes.

```python
from splint import SplintResult, attributes
import pathlib

@attributes(tag="file")
def check_file_exists():
    """ Verify this that my_file exists """
    status = pathlib.Path("myfile.csv").exists()
    return SplintResult(status=status, "Verify daily CSV file exists")


@attributes(tag="file")
def check_file_age():
    file = pathlib.Path("myfile.csv")
    modification_time = file.stat().st_mtime
    current_time = dt.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    status = file_age_in_hours < 24.0
    if file_age_in_hours < 24:
        return SplintResult(status=True, "The file age is OK {file_age_in_hours}")
    else:
        return SplintResult(status=False, "The file is stale")
```

And even a bit more complexity pass values to these functions using environments, which are very similar to `pytest`
fixtures.

```python

@environment('module')
def csv_file():
    return pathlib.Path("myfile.csv")


@attributes(tag="file")
def check_file_exists(csv_file):
    """ Verify this that my_file exists """
    return SplintResult(status=csv_file.exists(), "Verify daily CSV file exists")


@attributes(tag="file")
def check_file_age(csv_file):
    modification_time = csv_file.stat().st_mtime
    current_time = dt.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    status = file_age_in_hours < 24.0
    if file_age_in_hours < 24:
        return SplintResult(status=True, "The file age is OK {file_age_in_hours}")
    else:
        return SplintResult(status=False, "The file is stale")
```

## How is Splint Organized?

Splint uses the following hierarchy:

    `SplintPackage` (one or more SplintModules in a folder)
        `SplintModule` (one or more SplintFunctions in a Python file (function starting with the text "check_"))
            `SplintFunction` (when called will return 0 or more `SplintResults`)

Typically one works at the module or package level where you have python files that have 1 or more files with rules in
them.

Each Splint function returns 0-to-N results from its generator function. By convention, if None is returned, the rule
was skipped.
The rule functions that you write don't need to use generators. They can return a wide variety of output
(e.g., Boolean, List of Boolean, SplintResult, List of SplintResult), or you can write a generator that yields results
as they are checked.

## Rule Integrations

To simplify getting started there are some out of the box rules you can call to check files and folders on your file system
dataframes and web pages.  These integrations make many common checks 1-liners.

The rule shown below uses the rule_large_files function to look at all the files in a folder and report status on file
sizes > 100k.

```python
    @splint.attributes(tag="tag")
    def check_rule1():
        for result in splint.rule_large_files(folder="./log_files", pattern="log*.txt", max_size=10000):
            yield result
```

## What is the output?

The low level output of a `SplintFunction` are `SplintResults`. Each `SplintResult` is trivially converted to a `json`
record or a line in a CSV file for processing by other tools. It is very easy to connect things up to 
`Streamlit`, `FastAPI` or a `typer` CLI app by json-ifying the results.

## What are scores?

The idea of scoring is simple by the details are complex. Scores let you look at the results of all of your checks
and reduce it to number from 0 to 100. A simple percentage of pass fail results can work...but what if some rules are "
easy" while others are hard? What if some test have 100's of ways to fail (each line in a spreadsheet needs a comment) 
but has only one result when there are no failures?  It turns out you need weights and ways to aggregate results to 
make sense of these things.

Out of the box, most of these cases can be handled by choosing a scoring method. Currently, scoring happens globally,
but it is in work creating scoring by function.

## What are @attributes

Each rule function can be assigned attributes that define metadata about the rule function.  Attributes are at the heart
of how `splint` allows you to filter, sort, select tests to run and view.

 1. `tag` zero or more strings that can be used for filtering results.
 2. `phase` a single string that indicates a phase of testing/development
 3. `level` which is a numeric value that is better for greater than/less than tests
 4. `weight` a positive number indicating the weight of a functions results.  The nominal weight is 100.
 5. `skip` indicates the function should be skipped.
 6. `ruid` or rule-id is a unique identifier for a rule. If one test as a rule all of them must.
 7. `ttl_minutes` allow caching of results so expensive tests don't need to be rerun  which is only useful in cases where you run tests over and over


## What are Rule Ids (RUIDS)?

Tags and phases are generic information that is only present for filtering. The values don't mean much to the inner
workings of splint.  `RUID`s are different. The purpose of an `RUID` is to tag every rule function with a unique value
that is meaningful to the user. The only rule to the code is that they are unique. If you tag a single function with an
RUID the system will expect you to put a unique ID on every function. A `SplintException` is thrown if there are RUIDs
that are not unique.  

What do you get for this? You now have fine grain control to the function level AND the user level to enable/disable
checks. A `pylint` analogy is that you can turn off-line width checks globally for you project setting values in 
the `.lintrc` file. In the case of splint, perhaps part of your system has one set of rules and another part of 
the system has has the same set but some don't apply.
Or perhaps in an early phase development a subset of rules is applied, and at another a different set of rules is applied. 
RUIDS allow you to set this up with "simple" config files.

RUIDs can be anything hashable (but comme on, they should be short strings). Smart-ish values like File-001, Fill-002, '
smarter' or File-Required, File-Too-Old. Whatever makes sense on the project. As a general rule smart naming conventions 
aren't smart, so beware of the bed you make for yourself.


```python
@attributes(ruid="file_simple")
def check_file_age():
    f = pathlib.Path("/user/file1.txt")
    return SplintResult(status=f.exists(), msg=f"File {f.name}")


@attributes(ruid="file_complex")
def check_file_age():
    f = pathlib.Path("/user/file2.txt")
    return SplintResult(status=f.exists(), msg=f"File {f.name}")
```

## Splint RC

A `.splintrc` file can be provided in the toml format (or from code a dictionary) of the form

__WRITE DOCS HERE__



This TOML file has a "simple" mode and a "complex" mode. In each case they run all the checks (based on to include) 
and then anything in the exclude list is not reported. Note that this happens BEFORE the tests are run rather than 
running the test and then throwing away the result.

```toml
[simple]
include = ["*"]
exclude = ["file_complex"]

[complex]
include = ["*"]
exclude = ["file_simple"]
```

## TTL Time to Live Caching
If you have time-consuming checks you can put a ttl on it to reduce the number of times it is run. All you need to
do is tag the function with the `ttl_minutes` attribute, and it will use cached results if the call frequency is inside
the ttl that was specified.  This feature is useful in situations where you are splinting a system 
in real time for things like dashboards or long running tasks.  When you need it, it is very
useful.

The status during the ttl period wil be the last result.

```python
@attributes(ttl_minutes="1.0hr")
def check_file_age():
    pic = make_black_hole_image()
    yield(status=pic.black_hole_exists(),msg="Hourly cluster image generation check")
```

## How can these rules be organized?

Lots of ways.

1) Just give it a bunch of functions in a list would work.  Ideally the return SplintResults, but it works if they 
   return booleans or lists of booleans.
2) Point it to a file and `splint` will find all the functions in that file and call them. (ScruffModule)
3) Point it to a folder (or pass it a bunch of filenames) and splint will load each module and collect all the tests (
   ScruffPackage)

For me that is as deep as I want things to go.

## How are environments used?
__WRITE ME__

## WTH does `splint` derive from?

Splint is just a name that sounds cool. When I started this I thought system-lint.

## Command Line Demo App For `splinter`:

Included is a light weight `typer` app that allows to point splint at a file or folder and run all tests via the command
line.

To run it against a folder

`python -m splinter.py -p path/to/package_folder`

To run it against a folder and start a FastAPI endpoint do:

`python -m splinter.py -p path/to/package_folder --api --port 8000`

```text
Usage: splinter.py [OPTIONS]

 Run Splint checks on a given using a typer command line app.

╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --mod      -m      TEXT  The module to run rules against. [default: None]                                       │
│ --pkg      -p      TEXT  The package to run rules against. [default: None]                                      │
│ --json     -j      TEXT  The JSON file to write results to. [default: None]                                     │
│ --flat     -f            Should the output be flat or a hierarchy. [default: True]                              │
│ --score    -s            Print the score of the rules.                                                          │
│ --api                    Make rules visible to FastAPI Endpoint                                                 │
| --port                   FastAPI Port [default=8000]                                                            │
│ --verbose  -v            Enable verbose output.                                                                 │
│ --help                   Show this message and exit.                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

## FastAPI Interface

If you want your rule checking results to be runnable via a web API, you can use the `splinter.py` file to see how to
trivially create a fast API app from your code. There are no changes required from your code to support a
FastAPI interface. If you created `rule_ids` for all of your rule functions then they are all accessible via the
API. If you didn't use `ruids` then you can run the whole set of functions.  The sample command line app is meant to 
be a trivial example of how to hook up a `splint` ruleset to the web.

Because `splint` uses python dictionaries to move result data around, connecting to a FastAPI interface is trivial.
The `splinter` demo tool shows that this can be done with just a few lines of code to create an FastAPI interface.

Just run with the --api flag and you'll see `uvicorn` startup your  API.
```
/Users/chuck/splint/.venv/bin/python splinter.py --pkg . --api 
INFO:     Started server process [3091]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     127.0.0.1:64116 - "GET / HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:64116 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:64116 - "GET /openapi.json HTTP/1.1" 200 OK
```

And going to `localhost:8000/docs` gets you this:

FastAPI swagger interiface:
![FastAPI](./img/fastapi2.png)

FastAPI example running some rules:
![FastAPI](./img/fastapi.png)

## TODO

1. Improve environment parameters
2. Implement `.splintrc` file and toml interface.
3. Clean up exceptions in rule functions
4. Add streamlit example.
5. Make pip installable.
6. Fix issue with module having the same name.
7. By function scoring