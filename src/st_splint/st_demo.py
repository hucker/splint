"""
This example shows a NON-TRIVIAL example of how to use splint with streamlit.  An attempt is made
to use most of the major feature groups including:

1) Packages/Modules/Functions
2) Use of all attributes for classifying rule functions.
3) Use of attributes in non-trivial way for filtering
4) Use of "real" progress bar
5) Display of detailed results
6) Display of "scoreboard"
7) Display of the json
8) Rule functions returning various types of values.

"""


import streamlit as st

import src.splint as splint

st.set_page_config(layout='wide')


def color(c,t):
    return f':{c}[{t}]'
def green(text):
    return color('green',text)
def orange(text):
    return color('orange',text)
def blue(text):
    return color('blue',text)

def red(text):
    return color('red',text)
def violet(text):
    return color('violet',text)

def display_overview(checker: splint.SplintChecker) -> None:
    """
    Display the results from the checker in a scoreboard format.

    Args:
        checker: Splint checker
    """
    table_headers = "| Metric | Value |"
    table_separators = "|:----:|:----:|"

    # Define the data rows
    table_rows = [
        f"| {green('**SCORE**')} | {checker.score:0.1f}% |",
        f"| {green('**PASS**')} | {checker.pass_count} |",
        f"| {red('**FAIL**')} | {checker.fail_count} |",
        f"| {orange('**WARN**')} | {checker.warn_count} |",
        f"| {violet('**SKIP**')} | {checker.skip_count} |",
        f"| {blue('**TOTAL**')} | {checker.result_count} |",
    ]

    # Join headers, separators, and rows to form a complete Markdown table
    markdown_table = "\n".join([table_headers, table_separators, *table_rows])

    # Display the Markdown table in Streamlit
    st.markdown(markdown_table)

def yes_or_none(var):
    return 'Yes' if bool(var) else  ''

def display_results(results: list[splint.SplintResult]):
    """
    Display the results in a Markdown table

    Args:
        results: list of splint results
    """
    headers = ['Count', 'Status', 'Warn', 'Skipped', 'Tag', 'Level', 'Phase', 'RUID', 'Module Name', 'Function Name', 'Message']

    # Start with the table headers and separators created as f-strings
    table = [
        f"| {' | '.join(headers)} |",
        f"|{' :----: |' * len(headers)}"
    ]

    for count, r in enumerate(results, start=1):
        # Determine the status
        status = "Skipped" if r.skipped else "Pass" if r.status else "Fail"

        c_f = green if r.status else red if not r.skipped else orange

        # Append each row directly to the table
        table.append(
            f"| {count} | {c_f(r.status)} | {orange(yes_or_none(r.warn_msg))} | {violet(yes_or_none(r.skipped))}| {blue(r.tag)} | {r.level} | {r.phase} | {r.ruid} | {c_f(r.module_name)} | {c_f(r.func_name)} |{c_f(r.msg)} |")

    # Convert the list of rows into a single string with line breaks
    markdown_table = "\n".join(table)

    st.markdown(markdown_table)


def display_package_info(pkg, checker):
    """
    Displays information about the checked package and available options for checking.

    Args:
        pkg: The package being checked.
        checker: The checker setup for validating the package.
    """

    st.title('Splint Demo')

    # Define the table headers
    table_headers = "| **Item** | **Value** |"
    table_separators = "|:----:|:----:|"

    # Define the data rows
    table_rows = [
        f"| **Package** | {pkg.name} |",
        f"| **Module Count** | {pkg.module_count} |",
        f"| **Function Count** | {checker.function_count} |",
        f"| **Tags** | {','.join(checker.tags)} |",
        f"| **Rule IDs** | {','.join(checker.ruids)} |",
        f"| **Levels** | {checker.levels} |",
        f"| **Phases** | {','.join(checker.phases)} |",
    ]

    # Combine all parts to form the full table
    markdown_table = "\n".join([table_headers, table_separators] + table_rows)

    # Display the table
    st.markdown(markdown_table)


def display_json_results(checker: splint.SplintChecker):
    """
    Display the JSON results of the given `splint.SplintChecker` object.

    Args:
        checker: An instance of `splint.SplintChecker` containing the JSON results to be displayed.
    """
    st.write("JSON Results")
    with st.expander("Results:", expanded=True):
        st.json(checker.as_dict())


class SplintStreamlitProgressBar(splint.SplintProgress):
    """ Implementation of a progress bar for streamlit. """

    def __init__(self, progress_bar: st.progress):
        """ Store streamlit progress bar in global state"""
        self.progress_bar = progress_bar

    def __call__(self, current_count: int, max_count: int, msg: str, result=None):
        """
        Display a status message/progress update.  The progress bar goes from 0 to full
        scale as a percentage of the number of function that have run, that is whey
        we get current/max.  We also have a message which can be anything as well
        as a result which is the detailed results.  Presumably some progress systems
        would watch the result metadata while others would be content with the message.
        """
        if max_count <= 0:
            max_count = 1
        if current_count > max_count:
            current_count = max_count
        percent = current_count / float(max_count)
        percent = max(0, min(1.0, percent))
        self.progress_bar.progress(percent, msg)


def main():
    """
    Main method for running the Splint package checker.

    Usage:
        Run this method to run the Splint package checker. It prompts the user to select options for including or
        excluding functions based on tags, rule IDs, levels, and phases. After selecting the options,
        click the "Run Splint" button to start the rule checking process. The results will be displayed in the UI.

    Example:
        main()
    """

    packages_mapping = {
        "File System Checking": "../examples/file_system",
        "Generic": "../examples/my_package"
    }

    package_name = st.selectbox("Select Package", options=list(packages_mapping.keys()), index=0)
    package_folder = packages_mapping[package_name]

    package = splint.SplintPackage(folder=package_folder)
    checker = splint.SplintChecker(packages=[package], auto_setup=True)

    with st.container(border=True):
        with st.container(border=True):
            display_package_info(package, checker)
        include_ui = st.checkbox("Select Function to Run By Including Items", value=True)

        if include_ui:
            st.write(
                "All of these options are ANDed together, if you select everything from 1 of the lists all functions will be run.")
            tags = st.multiselect("Include These Tags", options=checker.tags, default=checker.tags)
            ruids = st.multiselect("Include These Rule Ids", options=checker.ruids, default=[])
            levels = st.multiselect('Include These Levels', options=checker.levels, default=[])
            phases = st.multiselect('Include These Phases', options=checker.phases, default=[])
        else:
            st.write(
                "All of these options are ANDed together, if you select everything from 1 of the lists no functions will be run.")
            tags = st.multiselect("Exclude These Tags", options=checker.tags, default=None)
            ruids = st.multiselect("Exclude These Rule Ids", options=checker.ruids, default=None)
            levels = st.multiselect('Exclude These Levels', options=checker.levels, default=None)
            phases = st.multiselect('Exclude These Phases', options=checker.phases, default=None)

    if st.button("Run Splint"):
        if include_ui:
            checker.include_by_attribute(tags=tags, ruids=ruids, levels=levels, phases=phases)
        else:
            checker.exclude_by_attribute(tags=tags, ruids=ruids, levels=levels, phases=phases)
        if len(checker.collected) == 0:
            st.warning("No rule functions found. It appears that you have filtered everything out.")
        else:
            prog_bar = st.progress(0, text=f"Rule checking status 0 of {checker.function_count}")

            # IInstall progress bar that is nice for splint.
            checker.progress_callback = SplintStreamlitProgressBar(prog_bar)

            # Magic happens here
            results: list[splint.SplintResult] = checker.run_all()

            with st.container(border=True):
                display_overview(checker)

            with st.container(border=True):
                display_results(results)

            with st.container(border=True):
                display_json_results(checker)


if __name__ == "__main__":
    main()
