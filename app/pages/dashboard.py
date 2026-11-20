import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests as http_requests
from datetime import datetime

API_BASE = "http://localhost:8000"


def render_dashboard():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard</h1>
        <p>Overview of medical analysis system</p>
    </div>
    """, unsafe_allow_html=True)

    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

    stats = {
        "total_predictions": 0, "total_patients": 0, "healthy_patients": 0,
        "average_confidence": 0, "today_reports": 0,
    }
    disease_data = {}
    monthly_data = []

    try:
        resp = http_requests.get(f"{API_BASE}/api/analytics/dashboard", headers=headers)
        if resp.status_code == 200:
            stats = resp.json()
        d_resp = http_requests.get(f"{API_BASE}/api/analytics/disease-distribution", headers=headers)
        if d_resp.status_code == 200:
            disease_data = d_resp.json()
        m_resp = http_requests.get(f"{API_BASE}/api/analytics/monthly-cases", headers=headers)
        if m_resp.status_code == 200:
            monthly_data = m_resp.json()
    except Exception:
        pass

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        (col1, "Patients Scanned", stats["total_patients"], "👤", ""),
        (col2, "Diseases Detected", stats["total_predictions"], "🦠", "danger"),
        (col3, "Healthy Patients", stats["healthy_patients"], "✅", "success"),
        (col4, "Avg Confidence", f"{stats['average_confidence']*100:.1f}%", "🎯", ""),
        (col5, "Today's Reports", stats["today_reports"], "📋", "warning"),
    ]
    for col, label, value, icon, extra_class in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card {extra_class}">
                <div style="font-size:1.5rem;">{icon}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Monthly Cases</div>', unsafe_allow_html=True)
        if monthly_data:
            months = [f"{d['year']}-{d['month']:02d}" for d in monthly_data]
            counts = [d["count"] for d in monthly_data]
            fig = px.line(x=months, y=counts, markers=True, labels={"x": "Month", "y": "Cases"})
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                height=300,
            )
            fig.update_traces(line_color="#0F766E", line_width=3)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available yet. Upload X-rays to see trends.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🦠 Disease Distribution</div>', unsafe_allow_html=True)
        if disease_data:
            labels = list(disease_data.keys())
            values = list(disease_data.values())
            colors = ["#0F766E", "#14B8A6", "#16A34A", "#F59E0B", "#DC2626", "#8B5CF6", "#EC4899", "#6366F1"]
            fig = go.Figure(data=[go.Pie(
                labels=labels, values=values, hole=0.4,
                marker=dict(colors=colors[:len(labels)]),
                textinfo="label+percent",
                textposition="outside",
            )])
            fig.update_layout(
                margin=dict(l=20, r=20, t=20, b=20),
                height=300,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No disease data yet.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🏥 Quick Actions</div>', unsafe_allow_html=True)
    qc1, qc2, qc3, qc4 = st.columns(4)
    with qc1:
        if st.button("📤 Upload New X-Ray", use_container_width=True):
            st.session_state.page = "Upload X-ray"
            st.rerun()
    with qc2:
        if st.button("📋 View Reports", use_container_width=True):
            st.session_state.page = "Reports"
            st.rerun()
    with qc3:
        if st.button("📁 Patient History", use_container_width=True):
            st.session_state.page = "History"
            st.rerun()
    with qc4:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.page = "Analytics"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;padding:2rem;color:#94A3B8;font-size:0.85rem;">
        <p>Medical Report AI v2.0 | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
    </div>
    """, unsafe_allow_html=True)
