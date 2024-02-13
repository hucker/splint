"""Trivial Typer App to run Splint checks on a given target."""
import sys
import pathlib
import typer
import json

s = pathlib.Path('./src').resolve()
sys.path.insert(0,str(s))
app = typer.Typer(add_completion=False)
import splint

def dump_results(results):
    """ Dump results to stdout """
    for result in results:
        typer.echo(result)


@app.command()
def run_checks(
    module: str = typer.Option(None, '-m','--mod', help="The module to run rules against."),
    pkg: str = typer.Option(None, '-p','--pkg', help="The package to run rules against."),
    json_file: str = typer.Option(None, '-j','--json', help="The JSON file to write results to."),
    flat: bool = typer.Option(True, '-f', '--flat', help="Should the output be flat or a hierarchy."),
    score: bool = typer.Option(False, '-s', '--score', help="Print the score of the rules."),
    verbose: bool = typer.Option(False, '-v', '--verbose', help="Enable verbose output.")
):
    """Run Splint checks on a given using a typer command line app."""

    options = {"module": module, "package": pkg}


    try:

        if module:
            target_path = pathlib.Path(module)
            if target_path.is_file():
                mod = splint.SplintModule(module_name=target_path.stem,module_file=str(target_path))
            else:
                typer.echo(f"Invalid module: {module}")
        else:
            mod = None

        if pkg:
            folder = pathlib.Path(pkg)
            if folder.is_dir():
                pkg = splint.SplintPackage(folder=folder)
            else:
                typer.echo(f"Invalid package: {pkg}")
        else:
            pkg = None

        # If they supply 1 or both they are all run since the checker can handle arbitrary combinations
        if mod or pkg:
            ch = splint.SplintChecker(modules=mod,packages=pkg)
            ch.pre_collect()
            ch.prepare()
            results = ch.run_all()
        else:
            typer.echo("Please provide a module, package to run checks on.")
            return

        if not results:
            typer.echo("There were no results.")
            return

        if not flat:
            results = splint.splint_result.group_by(results,['pkg_name','module_name','func_name'])

        if verbose:
            dump_results(results)
        else:
            typer.echo(splint.overview(results))

        if score:
            test_score = splint.ScoreByResult()
            typer.echo(f"Score: {test_score(results):.1f}")

        if json_file:
            d = splint.splint_result.results_as_dict(results)
            with open(json_file, 'w',encoding='utf-8') as f:
                json.dump(d, f, indent=2)


    except splint.SplintException as e:
        typer.echo(f"SplintException: {e}")

    # Crude
    except Exception as e:
        typer.echo(f"An error occurred: {e}")

if __name__ == "__main__":
    app()