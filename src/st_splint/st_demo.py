"""
This example shows a NON-TRIVIAL example of how to use splint with streamlit.  An attempt is made
to use most of the majore feature groups including:

1) Packages/Modules/Functions
2) Use of all attributes for classifying rule functions.
3) Use of attributes in non-trivial way for filtering
4) Use of "real" progress bar
5) Display of detailed results
6) Display of "scoreboard"
7) Display of the json
8) Rule functions returning various types of values.

"""

from typing import List

import streamlit as st

import src.splint as splint

st.set_page_config(layout='wide')

DEMO_TITLE = "Splint Demo"
TITLE_SPLINT_SETUP = "Splint Demo"
RESULT_MESSAGES = "Result Messages"
JSON_RESULTS = "JSON Results"
OVERVIEW_HEADER = "### Overview"


def display_overview(checker:splint.SplintChecker) -> None:
    """
    Display the results from the checker in a scoreboard format.

    Args:
        checker: Splint checker
    """
    table_headers = "| Metric | Value |"
    table_separators = "|:----:|:----:|"

    # Define the data rows
    table_rows = [
        "| :green[**SCORE**] | " + str(checker.score) + " |",
        "| :green[**PASS**] | " + str(checker.pass_count) + " |",
        "| :red[**FAIL**] | " + str(checker.fail_count) + " |",
        "| :orange[**SKIP**] | " + str(checker.skip_count) + " |",
        "| :blue[**Total**] | " + str(checker.total_count) + " |",
    ]

    # Combine the headers, separators, and rows to form the full table
    markdown_table = "\n".join([table_headers, table_separators] + table_rows)

    # Display the Markdown table in Streamlit
    st.markdown(markdown_table)

def display_results(results:List[splint.SplintResult]):
    """
    Display the results in a markdowntable

    Args:
        results: List of splint results
    """
    headers = ['Count', 'Status', 'Tag', 'Level', 'Phase', 'RUID', 'Module Name', 'Function Name', 'Message']

    # Create the table headers
    table_headers = "| " + " | ".join(headers) + " |"
    table_separators = "|:----:|" * len(headers)

    # Initialize the Markdown table with headers
    markdown_table = f"{table_headers}\n{table_separators}"

    for count, r in enumerate(results, start=1):
        # Determine the status
        status = "Skipped" if r.skipped else "Pass" if r.status else "Fail"

        # Create a table row
        row_data = [str(item) for item in [count, status, r.tag, r.level, r.phase, r.ruid, r.module_name, r.func_name, r.msg]]
        table_row = "| " + " | ".join(row_data) + " |"

        # Append the row to the Markdown table
        markdown_table += f"\n{table_row}"

    st.markdown(markdown_table)



def display_package_info(pkg, checker):
    """
    Displays information about the checked package and available options for checking.

    Args:
        pkg: The package being checked.
        checker: The checker setup for validating the package.
    """

    st.title(DEMO_TITLE)

    # Define the table headers
    table_headers = "| **Metric** | **Value** |"
    table_separators = "|:----:|:----:|"

    # Define the data rows
    table_rows = [
                     "| **Package** | " + str(pkg.name) + " |",
                     "| **Module Count** | " + str(pkg.module_count) + " |",
                     "| **Function Count** | " + str(checker.function_count) + " |",
                     "| **Tags Found** | " + str(checker.tags) + " |",
                     "| **Rule IDs Found** | " + str(checker.ruids) + " |",
                     "| **Levels** | " + str(checker.levels) + " |",
                     "| **Phases** | " + str(checker.phases) + " |",
                 ]

    # Combine all parts to form the full table
    markdown_table = "\n".join([table_headers, table_separators] + table_rows)

    # Display the table
    st.markdown(markdown_table)

def display_json_results(checker:splint.SplintChecker):
    """ Show the raw data from the json"""
    st.write(JSON_RESULTS)
    with st.expander("Results:", expanded=True):
        st.json(checker.as_dict())

def make_progress_bar(pb: st.progress, count):
    """ Progress bar to support streamlit notion of progress"""
    def progress(index, text, result=None):
        if count <= 0:
            value = 0
        else:
            value = float(index) / float(count)
        # make sure we are in range
        value = max(0.0, min(value,1.0))
        pb.progress(value, text)

    return progress

def main():
    pkg =  splint.SplintPackage(folder="./my_package")
    checker = splint.SplintChecker(packages=[pkg], auto_setup=True)

    with st.container(border=True):
        with st.container(border=True):
            display_package_info(pkg, checker)
        include_ui = st.checkbox("Select Function to Run By Including Items")

        if include_ui:
            tags = st.multiselect("Include These Tags", options=checker.tags, default=checker.tags)
            ruids = st.multiselect("Include These Rule Ids", options=checker.ruids, default=checker.ruids)
            levels = st.multiselect('Include These Levels', options=checker.levels, default=checker.levels)
            phases = st.multiselect('Include These Phases', options=checker.phases, default=checker.phases)
        else:
            tags = st.multiselect("Exclude These Tags", options=checker.tags,default=None)
            ruids = st.multiselect("Exclude These Rule Ids", options=checker.ruids,default=None)
            levels = st.multiselect('Exclude These Levels', options=checker.levels,default=None)
            phases = st.multiselect('Exclude These Phases', options=checker.phases,default=None)

    if st.button("Run Splint"):
        if include_ui:
            checker.include_by_attribute(tags=tags, ruids=ruids,levels=levels, phases=phases)
        else:
            checker.exclude_by_attribute(tags=tags, ruids=ruids,levels=levels, phases=phases)
        if len(checker.collected) == 0:
            st.warning("No rule functions found. It appears that you have filtered everything out.")
        else:
            prog_bar = st.progress(0, text=f"Rule checking status 0 of {checker.function_count}")

            # Note that make progress bar returns a function
            checker.progress_callback = make_progress_bar(prog_bar, checker.function_count)

            # Magic happens here
            results: List[splint.SplintResult] = checker.run_all()

            with st.container(border=True):
                display_overview(checker)

            with st.container(border=True):
                display_results(results)

            with st.container(border=True):
                display_json_results(checker)

if __name__ == "__main__":
    main()
