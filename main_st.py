import streamlit as st
import os
import sys

st.set_page_config(page_title="Oil Spill Detection App", layout="wide")

st.sidebar.title("App Selection")
app_mode = st.sidebar.radio("Choose App", ["📊 Detection App", "📋 Management Portal"])

def run_as_script(path):
    """Execute a python file as a script, setting __file__ correctly."""
    with open(path, encoding='utf-8') as f:
        code = compile(f.read(), path, 'exec')
        # Ensure the sub-script's folder is in the search path
        script_dir = os.path.dirname(os.path.abspath(path))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)
        # Execute with its own __file__
        exec(code, {"__name__": "__main__", "__file__": path, "st": st})

if app_mode == "📊 Detection App":
    path = os.path.join("ODA(OIL)", "oil_spill_detection", "oil_spill_detection", "detection_st.py")
    run_as_script(path)
else:
    path = os.path.join("OilSpillPortal", "portal_st.py")
    run_as_script(path)
