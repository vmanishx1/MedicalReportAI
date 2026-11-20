import streamlit as st
import requests as http_requests
import os

API_BASE = "http://localhost:8000"


def render_reports_page():
    st.markdown("""
    <div class="main-header">
        <h1>📋 Medical Reports</h1>
        <p>Generated PDF diagnostic reports</p>
    </div>
    """, unsafe_allow_html=True)

    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📄 Generated Reports</div>', unsafe_allow_html=True)

        try:
            resp = http_requests.get(f"{API_BASE}/api/predictions/history", headers=headers)
            if resp.status_code == 200:
                predictions = resp.json()
                if predictions:
                    for pred in predictions[:10]:
                        with st.container():
                            st.markdown(f"""
                            <div class="report-card">
                                <div style="display:flex;justify-content:space-between;align-items:center;">
                                    <div>
                                        <strong>{pred.get('patient_name', 'Unknown')}</strong>
                                        <span style="color:#64748B;font-size:0.85rem;margin-left:1rem;">
                                            {pred.get('patient_id', '')}
                                        </span>
                                    </div>
                                    <span class="badge badge-{pred.get('severity', 'info').lower()}">
                                        {pred.get('severity', 'N/A')}
                                    </span>
                                </div>
                                <div style="margin-top:0.5rem;font-size:0.85rem;color:#64748B;">
                                    {pred.get('created_at', '')[:10]} | 
                                    Diseases: {', '.join(pred.get('predictions', {}).get('detected_diseases', ['None']))}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            col_a, col_b = st.columns([1, 1])
                            with col_a:
                                if st.button(f"📥 Download PDF", key=f"dl_{pred['id']}", use_container_width=True):
                                    try:
                                        resp2 = http_requests.post(
                                            f"{API_BASE}/api/reports/generate",
                                            json={"prediction_id": pred["id"], "doctor_notes": ""},
                                            headers=headers,
                                        )
                                        if resp2.status_code == 200:
                                            st.success("Report generated! Check reports folder.")
                                        else:
                                            st.error("Failed")
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                            with col_b:
                                if st.button(f"🔍 View Details", key=f"view_{pred['id']}", use_container_width=True):
                                    st.session_state.prediction_result = pred
                                    st.session_state.page = "Predictions"
                                    st.rerun()
                            st.markdown("<hr style='margin:0.5rem 0;opacity:0.2;'>", unsafe_allow_html=True)
                else:
                    st.info("No reports generated yet. Upload and analyze an X-ray first.")
            else:
                st.info("Could not load reports")
        except Exception as e:
            st.warning(f"Could not connect to backend: {e}")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
        if st.button("📤 Upload New X-Ray", use_container_width=True):
            st.session_state.page = "Upload X-ray"
            st.rerun()
        if st.button("🔍 Latest Prediction", use_container_width=True):
            st.session_state.page = "Predictions"
            st.rerun()
        if st.button("📁 Patient History", use_container_width=True):
            st.session_state.page = "History"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Report Stats</div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="padding:0.5rem 0;">
            <p><strong>Total Reports:</strong> Loading...</p>
            <p><strong>Today:</strong> Loading...</p>
            <p><strong>Last 7 Days:</strong> Loading...</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
