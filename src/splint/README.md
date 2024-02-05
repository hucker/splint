# Splint

A "linting" tool for anything that isn't code.

IT was born when I realized that I subconcious  use pylint and ruff every day when I write code and it tells me whats wrong and I intuitively fix things.  I wanted to be able to press a button and have everything I know that must be true, actuall is true.

After many variations that looked like just writing a bunch of scripts that checked each thing, and then hooking in configuration files that tested all sorts of similar things conveniently I decided that what I wanted was to run something like pytest against various systems. `Pytest` does mostly what I want but it is really designed to solve a different problem.  I liked the declarative style of writing independent tests that get collected and run by a framework that managed the overhead of running tests, collecting results, reporting, filtering, and I wanted to build something outside of my box.

So I built splint.  If you know `pytes`t, you will be up and running quickly.  The basics are the same.  Splint has rules that live in files.  The rules are functions and they are loaded sort of like plugins to your app.  The functions you write can have decorators that add attributes to your rules to simplify reporting, and filtering.

The auto loaded modules and auto detected rule functions can take parameters.  These parameters work very similar to `pytest` in that they are detected and loaded from an environment that is dynamically built up from a hiearchy of your system.  It sound complicated, but if you get `pytes`t you will get splint.

## Why not pytest?
Good question.  `Pytes`t is huge and complicated while splint is small and simple.  Splint is made to drop into a command line app or a `streamlit` app with ease.  It is meant to be part of something else, plus I wanted to write something useful while learning about how plugin in files works.

## Getting Started

As I said, splint, works like `pytest`.  If you know `pytest`, you will be very good at `splint`. You write independent checks that can be run in any order to verify system state.  They should be atomic.   If you are used to writing tests with modules that start with "test" and functions that start with "test" it will be a breeze to get started. If you understand fixtures, that concept is also available through environments. Checks can be tagged with attributes so you can run various subsets of tests easily.  It is easy to write a trivial check with a single check function, but there is support for complete checking hierarchies.

From the most simple you could write rules like this:
```python
from splint import SplintResult,attributes

def check_equality()
    return True

def check_yielded_values():
    yield 1 == 1
    yield 2 != 1
```

As you might expect running this will provide 3 passing test results.

You can up the game and return status message info:
From the most simple you could write rules like this:
```python
from splint import SplintResult,attributes

def check_equality()
    return SplintResult(1==1,msg="Equality Check")

def check_yielded_values():
    yield SplintResult(status=1 == 1,msg="Equality Check")
    yield SplintResult(status=2 != 1,msg="Inequality Check")
```

As you might expect runing this will provide 3 passing test results.

Now we can add more comlexity.  Tag a test functions with attributes.
```python
from splint import SplintResult,attributes
import pathlib
import dt as datetime

@attributes(tag="file")
def check_file_exists():
    """ Verify this that my_file exists """
    status = pathlib.Path("myfile.csv").exists()
    return SplintResult(status=status,"Verify daily CSV file exists")

@attributes(tag="file")
def check_file_age():
    file = pathlib.Path("myfile.csv")
    modification_time = file.stat().st_mtime
    current_time = dt.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    status = file_age_in_hours < 24.0
    if file_age_in_hours < 24:
        return SplintResult(status=True,"The file age is OK {file_age_in_hours}")
    else:
        return SplintResult(status=False,"The file is stale")
```

And even a bit more complexity pass values to these functions using environments, which are very similar to fixutures.

```python


@environment('module')
def csv_file()
    return pathlib.Path("myfile.csv")

@attributes(tag="file")
def check_file_exists(csv_file):
    """ Verify this that my_file exists """
    return SplintResult(status=csv_file.exists(),"Verify daily CSV file exists")

@attributes(tag="file")
def check_file_age(csv_file):
    modification_time = csv_file.stat().st_mtime
    current_time = dt.now().timestamp()
    file_age_in_seconds = current_time - modification_time
    file_age_in_hours = file_age_in_seconds / 3600
    status = file_age_in_hours < 24.0
    if file_age_in_hours < 24:
        return SplintResult(status=True,"The file age is OK {file_age_in_hours}")
    else:
        return SplintResult(status=False,"The file is stale")
```


## What are SUIDS?
Tags and phases are generic information that is only present for filtering.  The values don't have much meaning to the inner
workings of splint.  `SUID`s are different.  The purpose of an `SUID` is to tag every check function with a unique value that
is meaningful to the end USER.  The only rule to the code is that they are unique.  If you tag a single function with an
SUID the system will expect you to put a unique ID on very function.  Exceptions are generated if there are SUIDs that are
not unique.

What do you get for this? You now have fine grain control to the function level AND the user level to enable/disable checks.
A code analogy is that you can turn off line width checks globally for you project setting values in the `.lintrc` file.  In the
case of splint, perhaps part of your system has one set of rules and another part of the system has a different set of rules.
The same code base with a different config file eanbling/disabling tests would be quite useful.

UIDs can be anything.  Simple integers starting from 1, smart-ish values like File-001, Fill-002, 'smarter' or File-Required,
File-Too-Old. Whatever makes sense on the project.  As a general rule smart naming conventions aren't smart, so beware of the
bed you make for yourself.

A `.splintrc` file can be provided in the toml format (or from code a dictionary) of the form

```python
@attributes(suid="file_simple")
def check_file_age():
    f = pathlib.Path("/user/file1.txt")
    return SplintResult(status=f.exists(),f"File {f.name}")

@attributes(suid="file_complex")
def check_file_age():
    f = pathlib.Path("/user/file2.txt")
    return SplintResult(status=f.exists(),f"File {f.name}")
```

```toml
[simple]
include = ["*"]
exclude = ["file_complex"]

[complex]
include = ["*"]
exclude = ["file_simple"]
```


## How can these rules be organized?

Lots of ways.

1) Just give it a bunch of functions in a list would work.
2) Point it to a file and splint will find all the functions in that file and call them. (ScruffModule)
3) Point it to a folder (or pass it a bunch of filenames) and splint will load each module and collect all the tests (ScruffPackage)
4) Point it to a folder of folders (or pass a list of folder names) and splint will load each module and collect all the tests (ScruffRepo)

For me that is as deep as I want things to go.

## How are environments

## WTH does splint derive from?

Splint is just a name that sounds cool.  When I started this I thought system-lint.

## Command Line Demo App For `splinter`:

Included is a light weight `typer` app that allows to point splint at a file, folder or repo (folder of folders) and run all tests via the command line.

To run it against a folder

`python -m splinter.py -p path/to/package_folder``


```text
Usage: splinter.py [OPTIONS]

 Run splint checks on a given target.


╭─ Options ─────────────────────────────────────────────────────────────────────────╮
│            -m      TEXT  The module to run checks on. [default: None]             │
│            -p      TEXT  The package to run checks on. [default: None]            │
│            -r      TEXT  The repo to run checks on. [default: None]               │
│ --verbose  -v            Enable verbose output.                                   │
│ --help                   Show this message and exit.                              │
╰───────────────────────────────────────────────────────────────────────────────────╯
```

## TODO
1. Add environment parameters
2. Clean up exceptions in check functions
3. Add fastapi example.
4. Add streamlit example.
5. Make pip installable.
6. Fix issue with module having the same name.