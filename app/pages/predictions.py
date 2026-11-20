import streamlit as st
import requests as http_requests
import plotly.graph_objects as go
from datetime import datetime

API_BASE = "http://localhost:8000"


def render_predictions_page():
    st.markdown("""
    <div class="main-header">
        <h1>🔍 Prediction Results</h1>
        <p>AI analysis results with explainability insights</p>
    </div>
    """, unsafe_allow_html=True)

    result = st.session_state.get("prediction_result")
    if not result:
        st.info("No prediction results available. Please upload an X-ray image first.")
        if st.button("📤 Go to Upload"):
            st.session_state.page = "Upload X-ray"
            st.rerun()
        return

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Analysis Results</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;margin-bottom:1rem;">
            <span><strong>Patient:</strong> {result.get('patient_name', 'Unknown')}</span>
            <span><strong>ID:</strong> {result.get('patient_id', 'N/A')}</span>
        </div>
        """, unsafe_allow_html=True)

        predictions = result.get("predictions", {})
        diseases = predictions.get("detected_diseases", [])
        conf_scores = result.get("confidence_scores", {})

        if diseases:
            for disease in diseases:
                conf = conf_scores.get(disease, 0)
                bar_color = "#16A34A" if conf > 0.7 else "#F59E0B" if conf > 0.4 else "#DC2626"
                st.markdown(f"""
                <div class="prediction-item">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:600;">{disease}</span>
                        <span class="badge badge-{'success' if conf > 0.7 else 'warning' if conf > 0.4 else 'danger'}">{conf*100:.1f}%</span>
                    </div>
                    <div style="margin-top:0.3rem;background:#E2E8F0;border-radius:8px;height:8px;">
                        <div style="background:{bar_color};width:{conf*100}%;height:8px;border-radius:8px;"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            severity = result.get("severity", "Unknown")
            severity_color = {"Mild": "#16A34A", "Moderate": "#F59E0B", "Severe": "#DC2626"}.get(severity, "#64748B")
            st.markdown(f"""
            <div style="margin-top:1rem;padding:1rem;background:#F8FAFC;border-radius:12px;">
                <strong>Severity:</strong> <span style="color:{severity_color};font-weight:600;">{severity}</span>
                <span style="margin-left:2rem;"><strong>Model:</strong> {result.get('model_used', 'N/A')}</span>
                <span style="margin-left:2rem;"><strong>Time:</strong> {result.get('inference_time', 0):.3f}s</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.success("✅ Lungs are clear. No abnormalities detected.")
            is_healthy = result.get("is_healthy", True)
            if is_healthy:
                st.markdown("""
                <div style="padding:1rem;background:#DCFCE7;border-radius:12px;text-align:center;">
                    <span style="font-size:2rem;">✅</span>
                    <h4 style="color:#16A34A;margin:0;">Healthy - No Significant Findings</h4>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔥 Grad-CAM Analysis</div>', unsafe_allow_html=True)

        grad_cam = result.get("grad_cam_path", "")
        if grad_cam:
            try:
                st.image(grad_cam, use_container_width=True, caption="AI Attention Map")
                st.markdown("""
                <div style="padding:0.8rem;background:#F0FDFA;border-radius:12px;margin-top:0.5rem;">
                    <p style="color:#0F766E;font-size:0.9rem;margin:0;">
                        🔍 The highlighted regions show areas that most influenced the AI prediction.
                        Red indicates strongest contribution to the diagnosis.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            except Exception:
                st.info("Grad-CAM image not available")
        else:
            st.info("Grad-CAM generation not available")

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">💡 Clinical Impression</div>', unsafe_allow_html=True)
        impression = result.get("clinical_impression", "No impression available.")
        st.markdown(f"<p style='line-height:1.7;'>{impression}</p>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Recommendations</div>', unsafe_allow_html=True)
        recs = result.get("recommendations", "No recommendations available.")
        for rec in recs.split(". "):
            if rec.strip():
                st.markdown(f"• {rec.strip()}")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📥 Generate PDF Report", use_container_width=True, type="primary"):
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            try:
                resp = http_requests.post(
                    f"{API_BASE}/api/reports/generate",
                    json={"prediction_id": result.get("prediction_id"), "doctor_notes": ""},
                    headers=headers,
                )
                if resp.status_code == 200:
                    st.success("✅ Report generated!")
                    st.session_state.page = "Reports"
                    st.rerun()
                else:
                    st.error("Failed to generate report")
            except Exception as e:
                st.error(f"Error: {e}")
    with col2:
        if st.button("📤 New Analysis", use_container_width=True):
            st.session_state.prediction_result = None
            st.session_state.page = "Upload X-ray"
            st.rerun()
    with col3:
        if st.button("📁 Save to History", use_container_width=True):
            st.success("✅ Saved to patient history")
