import streamlit as st
import requests as http_requests
from datetime import datetime

API_BASE = "http://localhost:8000"


def render_history_page():
    st.markdown("""
    <div class="main-header">
        <h1>📁 Patient History</h1>
        <p>Search and manage patient analysis history</p>
    </div>
    """, unsafe_allow_html=True)

    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

    search_query = st.text_input("🔍 Search by patient name, ID, or disease", placeholder="Type to search...")
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        if search_query:
            resp = http_requests.get(
                f"{API_BASE}/api/predictions/search",
                params={"query": search_query},
                headers=headers,
            )
        else:
            resp = http_requests.get(
                f"{API_BASE}/api/predictions/history",
                params={"skip": 0, "limit": 50},
                headers=headers,
            )

        if resp.status_code == 200:
            records = resp.json()
            if records:
                for record in records:
                    with st.container():
                        st.markdown(f"""
                        <div class="card" style="margin-bottom:0.8rem;">
                            <div style="display:flex;justify-content:space-between;align-items:center;">
                                <div>
                                    <h4 style="margin:0;color:#0F766E;">
                                        {record.get('patient_name', 'Unknown')}
                                    </h4>
                                    <p style="margin:0;color:#64748B;font-size:0.85rem;">
                                        ID: {record.get('patient_id', 'N/A')} |
                                        Date: {str(record.get('created_at', ''))[:10]}
                                    </p>
                                </div>
                                <div>
                                    <span class="badge badge-{record.get('severity', 'info').lower()}">
                                        {record.get('severity', 'N/A')}
                                    </span>
                                </div>
                            </div>
                            <div style="margin-top:0.5rem;">
                                <strong>Findings:</strong> {
                                    ', '.join(record.get('predictions', {}).get('detected_diseases', ['None']))
                                }
                            </div>
                            <div style="margin-top:0.8rem;">
                                <span style="color:#94A3B8;font-size:0.8rem;">
                                    Model: {record.get('model_used', 'N/A')} | 
                                    Confidence: {max(record.get('confidence_scores', {}).values(), default=0)*100:.1f}%
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col1:
                            if st.button("🔍 View", key=f"view_h_{record['id']}", use_container_width=True):
                                st.session_state.prediction_result = record
                                st.session_state.page = "Predictions"
                                st.rerun()
                        with col2:
                            if st.button("📥 Report", key=f"rpt_h_{record['id']}", use_container_width=True):
                                try:
                                    resp2 = http_requests.post(
                                        f"{API_BASE}/api/reports/generate",
                                        json={"prediction_id": record["id"], "doctor_notes": ""},
                                        headers=headers,
                                    )
                                    if resp2.status_code == 200:
                                        st.success("Report generated!")
                                except Exception:
                                    st.error("Failed")
                        with col3:
                            if st.button("🗑️ Delete", key=f"del_h_{record['id']}", use_container_width=True):
                                try:
                                    http_requests.delete(
                                        f"{API_BASE}/api/predictions/{record['id']}",
                                        headers=headers,
                                    )
                                    st.success("Deleted")
                                    st.rerun()
                                except Exception:
                                    st.error("Failed")

                        st.markdown("<hr style='margin:0.5rem 0;opacity:0.2;'>", unsafe_allow_html=True)
            else:
                st.info("No records found matching your search.")
        else:
            st.warning("Could not load history")
    except Exception as e:
        st.warning(f"Could not connect to backend: {e}")
        st.info("Ensure the backend server is running on port 8000")
