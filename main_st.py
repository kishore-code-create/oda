import streamlit as st

st.set_page_config(
    page_title="ODA Hub",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 ODA - Oil Detection & Analysis")
st.markdown("""
### Welcome to the Unified Dashboard
Use the **Sidebar on the left** to switch between:
1. **🛰️ Detection App**: Live hyperspectral & SAR oil detection.
2. **📋 Management Portal**: verified reports and history.

---
**Status:** 🔓 System Live
**Database:** ✅ Connected (Neon Cloud)
""")

st.sidebar.success("Select a page above.")
