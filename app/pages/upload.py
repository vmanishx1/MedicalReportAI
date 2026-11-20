import streamlit as st
import requests as http_requests
import tempfile
from pathlib import Path

API_BASE = "http://localhost:8000"


def render_upload_page():
    st.markdown("""
    <div class="main-header">
        <h1>📤 Upload Chest X-Ray</h1>
        <p>Upload a chest X-ray image for AI-powered analysis</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Patient Information</div>', unsafe_allow_html=True)

        with st.form("patient_form"):
            patient_name = st.text_input("Patient Name", placeholder="Enter full name")
            col_a, col_b = st.columns(2)
            with col_a:
                patient_age = st.number_input("Age", min_value=0, max_value=150, value=45)
            with col_b:
                patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-title">Upload Image</div>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Choose a Chest X-ray image",
                type=["png", "jpg", "jpeg"],
                help="Supported formats: PNG, JPEG, JPG. Max size: 20 MB",
            )

            if uploaded_file:
                st.image(uploaded_file, caption="Uploaded X-Ray", use_container_width=True)

            submitted = st.form_submit_button(
                "🔬 Analyze & Predict",
                use_container_width=True,
                type="primary",
                disabled=not uploaded_file,
            )

            if submitted and uploaded_file and patient_name:
                with st.spinner("🧠 Analyzing chest X-ray with AI..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                        data = {
                            "patient_name": patient_name,
                            "patient_age": patient_age,
                            "patient_gender": patient_gender,
                        }
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        resp = http_requests.post(
                            f"{API_BASE}/api/predictions/upload-predict",
                            files=files,
                            data=data,
                            headers=headers,
                        )
                        if resp.status_code == 200:
                            st.session_state.prediction_result = resp.json()
                            st.session_state.page = "Predictions"
                            st.success("✅ Analysis complete!")
                            st.rerun()
                        else:
                            st.error(f"Error: {resp.json().get('detail', 'Analysis failed')}")
                    except Exception as e:
                        st.error(f"Connection error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">ℹ️ Guidelines</div>', unsafe_allow_html=True)
        st.markdown("""
        **📋 Requirements:**
        - Format: PNG, JPEG, JPG
        - Max size: 20 MB
        - Clear chest X-ray (PA/AP view)
        
        **🔬 AI Detects:**
        - Pneumonia, COVID-19, Tuberculosis
        - Pleural Effusion, Cardiomegaly
        - Edema, Atelectasis, Consolidation
        - Mass, Nodule, Fibrosis
        
        **📊 Output Includes:**
        - Disease detection & probability
        - Severity assessment
        - Grad-CAM visualization
        - Clinical impression
        - Recommendations
        - PDF report
        """)
        st.markdown('</div>', unsafe_allow_html=True)
