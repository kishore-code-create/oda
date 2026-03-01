import streamlit as st
import os
import sys

# Bridge to the real portal script
path = os.path.join("OilSpillPortal", "portal_st.py")
if not os.path.exists(path):
    st.error(f"Cannot find: {path}")
else:
    # Add script dir to path
    script_dir = os.path.dirname(os.path.abspath(path))
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)
        
    with open(path, encoding='utf-8') as f:
        exec(f.read(), {"__name__": "__main__", "__file__": path, "st": st})
