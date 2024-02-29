from typing import List

import streamlit as st

import src.splint as splint


TITLE_SPLINT_SETUP = "Splint Setup Demo"
RESULT_MESSAGES = "Result Messages"
JSON_RESULTS = "JSON Results"


def display_overview(checker):
    st.markdown("## Overview")
    st.markdown(f"#### :green[SCORE]: {checker.score}")
    st.markdown(f"#### :green[PASS]: {checker.pass_count}")
    st.markdown(f"#### :red[FAIL]: {checker.fail_count}")
    st.markdown(f"#### :orange[SKIP]: {checker.skip_count}")
    st.markdown(f"#### :green[Total]: {checker.total_count}")


def display_messages(results):
    st.write(RESULT_MESSAGES)
    for count, result in enumerate(results, start=1):
        if result.skipped:
            msg = (f"{count} :orange[Skipped] {result.module_name}--{result.func_name}  {result.msg}")
        elif result.status:
            msg = (f"{count} :green[Pass] {result.module_name}--{result.func_name}  {result.msg}")
        else:
            msg = (f"{count} :red[Fail] {result.module_name}--{result.func_name}  {result.msg}")
        st.markdown(msg, help=result.doc)

def display_package_info(pkg, checker):
    """
    Displays information about the checked package and available options for checking.

    Args:
        pkg: The package being checked.
        checker: The checker setup for validating the package.
    """

    st.title("Splint Setup Demo")
    st.markdown(f"Load `{pkg.name}` package")
    st.markdown(f"Loaded `{pkg.module_count}` modules")
    for module in pkg.modules:
        st.markdown(f"Loaded `{module.module_name}` loaded `{module.check_function_count}` rule functions.")

    st.markdown(f"Tags found = `{checker.tags}`")
    st.markdown(f"Rule IDs found = `{checker.ruids}`")
    st.markdown(f"Levels = `{checker.levels}`")

def display_json_results(checker):
    st.write(JSON_RESULTS)
    with st.expander("Results:", expanded=True):
        st.json(checker.as_dict())

def make_progress_bar(pb: st.progress, count):
    def progress(index, text, result=None):
        value = float(index) / float(count)
        pb.progress(value, text)

    return progress


def main():
    pkg = splint.SplintPackage(folder="./package")
    checker = splint.SplintChecker(packages=[pkg], auto_setup=True)

    with st.container(border=True):
        with st.container(border=True):
            display_package_info(pkg, checker)

        tag = st.selectbox("Tag", checker.tags)
        ruids = st.multiselect("Rule Ids", options=checker.ruids)
        levels = st.multiselect('Levels', options=checker.levels)

        run_me = st.button("Run")

    if run_me:
        prog_bar = st.progress(0, text=f"Rule checking status 0 of {checker.function_count}")
        checker.progress_callback = make_progress_bar(prog_bar, checker.function_count)
        results: List[splint.SplintResult] = checker.run_all()

        with st.container(border=True):
            display_overview(checker)

        with st.container(border=True):
            display_messages(results)

        with st.container(border=True):
            display_json_results(checker)

if __name__ == "__main__":
    main()
