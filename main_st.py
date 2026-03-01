import streamlit as st
import os
import sys

# Add subdirectories to path so imports work
sys.path.append(os.path.join(os.getcwd(), "OilSpillPortal"))
sys.path.append(os.path.join(os.getcwd(), "ODA(OIL)", "oil_spill_detection", "oil_spill_detection"))

st.set_page_config(page_title="Oil Spill Detection App", layout="wide")

st.sidebar.title("App Selection")
app_mode = st.sidebar.radio("Choose App", ["📊 Detection App", "📋 Management Portal"])

if app_mode == "📊 Detection App":
    # Execute the detection script
    with open(os.path.join("ODA(OIL)", "oil_spill_detection", "oil_spill_detection", "detection_st.py"), encoding='utf-8') as f:
        exec(f.read())
else:
    # Execute the portal script
    with open(os.path.join("OilSpillPortal", "portal_st.py"), encoding='utf-8') as f:
        exec(f.read())
