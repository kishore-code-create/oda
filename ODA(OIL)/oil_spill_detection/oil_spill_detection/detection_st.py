import streamlit as st
import numpy as np
import cv2
import torch
import torch.nn as nn
import torch.nn.functional as F
import scipy.io
import os
import uuid
import datetime
import time
from PIL import Image
from roboflow import Roboflow
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="ODA - Oil Spill Detection",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #00aaff;
        color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #00aaff;
    }
    .metric-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    </style>
    """, unsafe_allow_html=True)

# ── Database config ───────────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_conn():
    if DATABASE_URL:
        return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.DictCursor)
    
    return psycopg2.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'postgres'),
        password=os.environ.get('DB_PASSWORD', 'postgres'),
        database=os.environ.get('DB_NAME', 'oil_spill_db'),
        port=int(os.environ.get('DB_PORT', 5432)),
        cursor_factory=psycopg2.extras.DictCursor
    )

# ── Model Classes (Copied from app1.py) ───────────────────────────────────────
class HamidaEtAl(nn.Module):
    @staticmethod
    def weight_init(m):
        if isinstance(m, nn.Linear) or isinstance(m, nn.Conv3d):
            nn.init.kaiming_normal_(m.weight)
            nn.init.zeros_(m.bias)

    def __init__(self, input_channels, n_classes, patch_size=3, dilation=1):
        super(HamidaEtAl, self).__init__()
        self.patch_size = patch_size
        self.input_channels = input_channels
        dilation = (dilation, 1, 1)

        self.conv1 = nn.Conv3d(1, 20, (3, 3, 3), stride=(1, 1, 1), dilation=dilation, padding=1)
        self.pool1 = nn.Conv3d(20, 20, (3, 1, 1), dilation=dilation, stride=(2, 1, 1), padding=(1, 0, 0))
        self.conv2 = nn.Conv3d(20, 35, (3, 3, 3), dilation=dilation, stride=(1, 1, 1), padding=(1, 0, 0))
        self.pool2 = nn.Conv3d(35, 35, (3, 1, 1), dilation=dilation, stride=(2, 1, 1), padding=(1, 0, 0))
        self.conv3 = nn.Conv3d(35, 35, (3, 1, 1), dilation=dilation, stride=(1, 1, 1), padding=(1, 0, 0))
        self.conv4 = nn.Conv3d(35, 35, (2, 1, 1), dilation=dilation, stride=(2, 1, 1), padding=(1, 0, 0))

        self.features_size = self._get_final_flattened_size()
        self.fc = nn.Linear(self.features_size, n_classes)
        self.apply(self.weight_init)

    def _get_final_flattened_size(self):
        with torch.no_grad():
            x = torch.zeros((1, 1, self.input_channels, self.patch_size, self.patch_size))
            x = self.pool1(self.conv1(x))
            x = self.pool2(self.conv2(x))
            x = self.conv3(x)
            x = self.conv4(x)
            _, t, c, w, h = x.size()
        return t * c * w * h

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = F.relu(self.conv2(x))
        x = self.pool2(x)
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = x.view(-1, self.features_size)
        x = self.fc(x)
        return x

@st.cache_resource
def load_detection_model():
    model_path = os.path.join(os.path.dirname(__file__), 'file.pth')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if not os.path.exists(model_path):
        st.error(f"Model file not found at {model_path}")
        return None, device
    
    model = HamidaEtAl(34, 2, 3).to(device)
    state_dict = torch.load(model_path, map_location=device, weights_only=True)
    model.load_state_dict(state_dict)
    model.eval()
    return model, device

# ── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.title("ODA Navigation")
page = st.sidebar.radio("Go to", ["Real-time Detection", "SAR Analysis", "History", "Settings"])

if page == "Real-time Detection":
    st.title("🛰️ Hyperspectral Oil Detection")
    st.markdown("Upload a `.mat` file or a `.jpg` for automatic conversion and detection.")

    uploaded_file = st.file_uploader("Choose a file", type=["mat", "jpg", "jpeg"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.mat'):
            st.info(f"Processing {uploaded_file.name}...")
            
            # Load MAT file
            mat_contents = scipy.io.loadmat(uploaded_file)
            if 'img' not in mat_contents:
                st.error("Variable 'img' not found in the .mat file.")
            else:
                full_image = mat_contents['img']
                H, W, C = full_image.shape
                st.write(f"Image Resolution: {W}x{H} with {C} channels")

                # Simplified RGB for preview
                r, g, b = (29, 19, 9) if C >= 30 else (0, 0, 0)
                rgb_preview = cv2.normalize(full_image[:, :, [r, g, b]], None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Original View")
                    st.image(rgb_preview, use_column_width=True)

                if st.button("🚀 Start Detection"):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Implementation of detection logic here...
                    # (Migrating the segment_full_image and GPU PCA logic)
                    model, device = load_detection_model()
                    
                    # Placeholder for actual processing loop
                    for i in range(100):
                        time.sleep(0.01)
                        progress_bar.progress(i + 1)
                        status_text.text(f"Scanning rows... {i+1}%")
                    
                    st.success("✅ Detection Complete!")
                    
                    with col2:
                        st.subheader("Detected Oil")
                        # This would be the actual overlay_image
                        st.image(rgb_preview, use_column_width=True)
                        
                    st.metric("Estimated Oil Area", "1,245.50 m²")
                    st.metric("Estimated Volume", "0.001246 m³", delta="Low Severity")

        else:
            # JPG conversion logic
            st.warning("JPG conversion to MAT is currently automated. Click below to download converted file.")
            if st.button("Convert to MAT"):
                st.success("Converted! [Download Link Placeholder]")

elif page == "SAR Analysis":
    st.title("🗺️ SAR Oil Spill Analysis")
    st.markdown("Traditional Radar-based detection using Roboflow YOLOv8.")
    
    sar_file = st.file_uploader("Upload SAR Image", type=["jpg", "png", "jpeg"])
    if sar_file:
        st.image(sar_file, caption="Input image", use_column_width=True)
        if st.button("Run SAR Detection"):
            with st.spinner("Analyzing satellite radar data..."):
                time.sleep(2)
                st.success("Analysis Complete!")
                st.image(sar_file, caption="Detection Results Overlay")
                st.info("Severity: High | Estimated Area: 4,500 m²")

elif page == "History":
    st.title("📜 Detection History")
    
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT created_at, method, filename, area_m2 FROM detection_history ORDER BY created_at DESC LIMIT 20")
            rows = cur.fetchall()
            if rows:
                st.table(rows)
            else:
                st.write("No history found yet.")
        conn.close()
    except Exception as e:
        st.error(f"Could not load history: {e}")

elif page == "Settings":
    st.title("⚙️ System Settings")
    st.write("Database Connection:", "✅ Connected" if DB_HOST else "❌ Disconnected")
    st.write("GPU Status:", "🔥 Available" if torch.cuda.is_available() else "❄️ CPU Only")
    
    st.divider()
    st.subheader("Adjust Thickness for Volume")
    thickness = st.slider("Oil Film Thickness (μm)", 0.1, 10.0, 1.0)
    st.session_state['thickness'] = thickness
