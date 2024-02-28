from typing import List

import streamlit as st
import src.splint as splint
def main():
    st.title("Streamlit Demo")

    pkg = splint.SplintPackage(folder="./package")
    ch = splint.SplintChecker(packages=[pkg],auto_setup=True)
    ch.ruids()

    st.markdown(f"Load `{pkg.name}` package")
    st.markdown(f"Loaded `{pkg.module_count}` modules")
    for module in pkg.modules:
        st.markdown(f"Loaded `{module.module_name}` loaded `{module.check_function_count}` rule functions.")

    st.markdown(f"Tags found = `{ch.tags()}`")
    st.markdown(f"Rule IDs found = `{ch.ruids()}`")


    tag = st.selectbox("Tag",ch.tags())
    ruids = st.multiselect("Rule Ids",options=ch.ruids())

    run_me = st.button("Run")
    if run_me:
        results:List[splint.SplintResult] = ch.run_all()

        st.write("## Overview")
        st.write(f"SCORE: {ch.score}")
        st.write(f"PASS: {ch.pass_count}")
        st.write(f"FAIL: {ch.fail_count}")
        st.write(f"Total: {ch.total_count}")

        st.write("## Result Messages")
        for count,result in enumerate(results,start=1):
            msg = (f"{count} {':green[PASS]'if result.status else ':red[FAIL]'} {result.module_name}--{result.func_name}  {result.msg}")
            st.markdown(msg)

        st.write("## JSON Results")
        with st.expander("Results:",expanded=True):
            st.json(ch.as_dict())


if __name__ == "__main__":
    main()