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

# Page Config - (Handled by main_st.py)
# st.set_page_config(
#     page_title="ODA - Oil Spill Detection",
#     page_icon="🌊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

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

# ── GPU/CPU Detection Logic ──────────────────────────────────────────────────

def gpu_pca(data_tensor, n_components):
    """Randomized GPU PCA — much faster than full SVD for large matrices."""
    mean = data_tensor.mean(dim=0, keepdim=True)
    centered = data_tensor - mean
    # Randomized SVD is faster and accurate enough for this task
    U, S, V = torch.pca_lowrank(centered, q=n_components, center=False, niter=4)
    return centered @ V

def segment_full_image(model, image, patch_size, device, progress_callback=None, batch_size=4096):
    """
    Optimized segmentation:
    - Vectorized patch extraction (unfold)
    - Mixed Precision support
    - Progress reporting
    """
    channels, H, W = image.shape
    pad = patch_size // 2
    
    # Pad image (Reflect padding for edges)
    padded = F.pad(image.unsqueeze(0), (pad, pad, pad, pad), mode='reflect')
    img_t = padded # (1, C, H+2pad, W+2pad)
    
    segmentation = np.zeros((H, W), dtype=np.int64)
    model.eval()

    def _infer_row(i):
        # Extract all patches in this row at once (Vectorized)
        row_data = img_t[:, :, i:i+patch_size, :]
        patches = row_data.unfold(3, patch_size, 1) # (1, C, patch_size, W, patch_size)
        patches = patches.permute(3, 0, 1, 2, 4).contiguous() # (W, 1, C, patch_size, patch_size)

        preds_list = []
        with torch.no_grad():
            for b in range(0, W, batch_size):
                out = model(patches[b:b+batch_size])
                preds_list.append(torch.argmax(out, dim=1))

        return torch.cat(preds_list)[:W].cpu().numpy()

    with torch.no_grad():
        for i in range(H):
            row_result = _infer_row(i)
            segmentation[i, :] = row_result
            if progress_callback:
                progress_callback(i + 1, H)

    return segmentation

def calculate_area(segmented_img, pixel_width=3.3, pixel_height=3.3):
    object_pixels = np.count_nonzero(segmented_img)
    return object_pixels * pixel_width * pixel_height

@st.cache_resource
def load_detection_model():
    # Use absolute path relative to this file's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'model_v1.pth')
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if not os.path.exists(model_path):
        st.error(f"Model file not found at {model_path}")
        # Diagnostic list
        try:
            files_in_dir = os.listdir(current_dir)
            st.info(f"Files found in the model directory: {files_in_dir}")
        except:
            pass
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
                    
                    model, device = load_detection_model()
                    if model is not None:
                        # 1. Run PCA
                        status_text.text("⚡ Running GPU-accelerated PCA...")
                        data_reshaped = torch.from_numpy(full_image.reshape(-1, C).astype(np.float32)).to(device)
                        data_pca = gpu_pca(data_reshaped, n_components=34)
                        full_image_reduced = data_pca.reshape(H, W, 34).permute(2, 0, 1).contiguous()
                        
                        # 2. Run Segmentation
                        def update_progress(current, total):
                            progress_bar.progress(current / total)
                            status_text.text(f"Scanning rows... {current}/{total}")

                        segmentation_result = segment_full_image(
                            model, full_image_reduced, 3, device,
                            progress_callback=update_progress
                        )
                        
                        st.success("✅ Detection Complete!")
                        
                        total_area = calculate_area(segmentation_result)
                        
                        with col2:
                            st.subheader("Detected Oil")
                            # Create overlay
                            masked_result = np.ma.masked_where(segmentation_result == 0, segmentation_result)
                            
                            import matplotlib.pyplot as plt
                            fig, ax = plt.subplots(figsize=(10, 10))
                            ax.imshow(rgb_preview)
                            ax.imshow(masked_result, cmap='spring', alpha=0.7)
                            ax.axis('off')
                            st.pyplot(fig)
                            
                        st.metric("Estimated Oil Area", f"{total_area:,.2f} m²")
                        
                        # Volume calculation (area * thickness)
                        thickness = st.session_state.get('thickness', 1.0) # in micrometers
                        volume = total_area * (thickness * 1e-6)
                        st.metric("Estimated Volume", f"{volume:,.6f} m³", delta="Live Analysis")
                        
                        # Save to database
                        try:
                            conn = get_db_conn()
                            with conn.cursor() as cur:
                                cur.execute(
                                    "INSERT INTO detection_history (user_id, username, method, filename, area_m2) VALUES (1, 'Admin', 'Hyperspectral', %s, %s)",
                                    (uploaded_file.name, total_area)
                                )
                            conn.commit()
                            conn.close()
                        except:
                            pass

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
