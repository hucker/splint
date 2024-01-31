"""Trivial Typer App to run Splint checks on a given target."""
import sys
import pathlib
s = pathlib.Path('./src').resolve()
sys.path.insert(0,str(s))

import typer
import splint
import pathlib
import glob
import json

app = typer.Typer(add_completion=False)

def dump_results(results):
    """ Dump results to stdout """
    for result in results:
        typer.echo(result)

def run_checks_on_module(module: str):
    """ Run checks on a module"""
    target_path = pathlib.Path(module)
    if target_path.is_file():
        mod = splint.SplintModule(module_name=target_path.stem,module_file=str(target_path))
        results = mod.run_all()
        return results
    else:
        typer.echo(f"Invalid module: {module}")

def run_checks_on_package(pkg: str):
    """ Run checks on a package"""
    folder = pathlib.Path(pkg)
    pkg = splint.SplintPackage(folder=folder)
    if folder.is_dir():
        results = pkg.run_all()
        return results
    else:
        typer.echo(f"Invalid package: {pkg}")

def run_checks_on_repo(repo: str):
    """ Run checks on a repo
    TODO: THis is not functional
    """
    if 1:
        raise splint.SplintException("Repo not implimented.")
    target_path = pathlib.Path(repo)
    if target_path.is_dir():
        for check_folder in glob.glob(str(target_path / 'check*')):
            for module in pathlib.Path(check_folder).rglob('*.py'):
                s.run_checks(str(module))
    else:
        typer.echo(f"Invalid repo: {repo}")

@app.command()
def run_checks(
    module: str = typer.Option(None, '-m','--mod', help="The module to run rules against."),
    pkg: str = typer.Option(None, '-p','--pkg', help="The package to run rules against."),
    repo: str = typer.Option(None,'-r','--repo', help="The repo to run rules against."),
    json_file: str = typer.Option(None, '-j','--json', help="The JSON file to write results to."),
    flat: bool = typer.Option(True, '-f', '--flat', help="Should the output be flat or a hierachy."),
    verbose: bool = typer.Option(False, '-v', '--verbose', help="Enable verbose output.")
):
    """Run Splint checks on a given using a typer command line app."""

    options = {"module": module, "package": pkg, "repo": repo}
    selected_options = {k: v for k, v in options.items() if v is not None}

    if len(selected_options) > 1:
        typer.echo("Please provide only one of module, package, or repo.")
        return

    if not selected_options:
        typer.echo("Please provide a module, package, or repo to run checks on.")
        return

    try:
        if module:
            results = run_checks_on_module(module)
        elif pkg:
            results = run_checks_on_package(pkg)
        elif repo:
            results = run_checks_on_repo(repo)

        if not flat:
            results = splint.splint_result.group_by(results,["repo_name",'pkg_name','module_name','func_name'])
            
        if verbose:
            dump_results(results)
        else:
            typer.echo(splint.overview(results))

        if json_file:
            d = splint.splint_result.results_as_dict(results)
            with open(json_file, 'w',encoding='utf-8') as f:
                json.dump(d, f, indent=2)


    except splint.SplintException as e:
        typer.echo(f"SplintException: {e}")
    except Exception as e:
        typer.echo(f"An error occurred: {e}")

if __name__ == "__main__":
    app()