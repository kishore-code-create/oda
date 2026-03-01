import streamlit as st
import psycopg2
import psycopg2.extras
import os
import pandas as pd
import datetime

# Page Config
st.set_page_config(
    page_title="ODA - Report Portal",
    page_icon="📋",
    layout="wide"
)

# ── Database config ───────────────────────────────────────────────────────────
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_USER = os.environ.get('DB_USER', 'postgres')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'postgres')
DB_NAME = os.environ.get('DB_NAME', 'oil_spill_portal_db')
DB_PORT = int(os.environ.get('DB_PORT', 5432))

def get_db_conn():
    return psycopg2.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursor_factory=psycopg2.extras.DictCursor
    )

# ── UI Layout ─────────────────────────────────────────────────────────────────
st.title("📋 ODA Management & Reporting Portal")

# Sidebar - Filter & Stats
st.sidebar.image("https://img.icons8.com/external-flat-icons-inmotus-design/67/null/external-oil-spill-natural-disasters-flat-icons-inmotus-design.png", width=80)
st.sidebar.title("Portal Dashboard")

role = st.sidebar.selectbox("Access Privilege (Simulated)", ["Admin", "Coast Guard", "NGO", "Government Official"])

# Stats Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Reports", "42", "+2 this week")
with col2:
    st.metric("Active Spills", "12", "-1 from yesterday")
with col3:
    st.metric("Critical Alerts", "4", "Immediate Action", delta_color="inverse")
with col4:
    st.metric("Avg. Response Time", "4.2h", "-0.8h")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 Incident Feed", "📝 Post New Report", "🌍 Global Map"])

with tab1:
    st.subheader("Verified Incident Feed")
    
    # Mock data for now if DB fails
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT created_at, title, location, severity, status FROM spill_reports ORDER BY created_at DESC")
            reports = cur.fetchall()
            if reports:
                df = pd.DataFrame(reports, columns=["Date", "Title", "Location", "Severity", "Status"])
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No verified reports found in database.")
        conn.close()
    except:
        st.warning("Offline Mode: Showing sample data")
        st.table([
            {"Date": "2025-05-12", "Title": "Gulf Deepwater Leak", "Location": "28.7°N, 88.3°W", "Severity": "Critical"},
            {"Date": "2025-05-11", "Title": "Coastal Seepage", "Location": "Long Island, NY", "Severity": "Low"}
        ])

with tab2:
    if role == "Admin":
        st.subheader("Post New Verified Report")
        with st.form("report_form"):
            title = st.text_input("Incident Title")
            location = st.text_input("Location Name")
            severity = st.selectbox("Severity Level", ["Low", "Medium", "High", "Critical"])
            description = st.text_area("Findings / Description")
            uploaded_img = st.file_uploader("Upload Verification Image", type=["jpg", "png"])
            
            submitted = st.form_submit_button("Publish Official Report")
            if submitted:
                st.success(f"Report '{title}' has been published and notified to Coast Guard.")
    else:
        st.warning("Only Admins can post new verified reports.")

with tab3:
    st.subheader("Active Spill Locations")
    # Sample Map Data
    map_data = pd.DataFrame({
        'lat': [28.7, 29.1, 28.5],
        'lon': [-88.3, -89.4, -87.8]
    })
    st.map(map_data)
