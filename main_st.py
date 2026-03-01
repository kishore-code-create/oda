import streamlit as st
import os
import sys
import traceback

# CRITICAL: set_page_config MUST be the very first st command
st.set_page_config(page_title="Oil Spill Detection App", layout="wide")

try:
    st.title("🌊 ODA - Multi-App Dashboard")

    st.sidebar.title("Navigation")
    app_mode = st.sidebar.radio("Choose Service", ["📊 Detection App", "📋 Management Portal"])

    def run_as_script(path):
        """Execute a python file as a script with clear error reporting."""
        if not os.path.exists(path):
            st.error(f"File not found: {path}")
            return
            
        try:
            with open(path, encoding='utf-8') as f:
                code_content = f.read()
                
                # Setup context
                script_dir = os.path.dirname(os.path.abspath(path))
                if script_dir not in sys.path:
                    sys.path.insert(0, script_dir)
                
                # Execute
                exec_globals = {
                    "__name__": "__main__",
                    "__file__": path,
                    "st": st
                }
                exec(code_content, exec_globals)
        except Exception as e:
            st.error(f"Crash in {os.path.basename(path)}")
            st.warning("Error Details:")
            st.exception(e)

    if app_mode == "📊 Detection App":
        path = os.path.join("ODA(OIL)", "oil_spill_detection", "oil_spill_detection", "detection_st.py")
        run_as_script(path)
    else:
        path = os.path.join("OilSpillPortal", "portal_st.py")
        run_as_script(path)

except Exception as ex:
    st.error("Fatal Dashboard Error")
    st.code(traceback.format_exc())
