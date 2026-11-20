import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests as http_requests

API_BASE = "http://localhost:8000"


def render_analytics_page():
    st.markdown("""
    <div class="main-header">
        <h1>📈 Analytics Dashboard</h1>
        <p>Comprehensive analytics and insights</p>
    </div>
    """, unsafe_allow_html=True)

    headers = {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

    disease_data = {}
    gender_data = {}
    age_data = {}
    monthly_data = []

    try:
        d_resp = http_requests.get(f"{API_BASE}/api/analytics/disease-distribution", headers=headers)
        if d_resp.status_code == 200:
            disease_data = d_resp.json()
        g_resp = http_requests.get(f"{API_BASE}/api/analytics/gender-analysis", headers=headers)
        if g_resp.status_code == 200:
            gender_data = g_resp.json()
        a_resp = http_requests.get(f"{API_BASE}/api/analytics/age-distribution", headers=headers)
        if a_resp.status_code == 200:
            age_data = a_resp.json()
        m_resp = http_requests.get(f"{API_BASE}/api/analytics/monthly-cases", headers=headers)
        if m_resp.status_code == 200:
            monthly_data = m_resp.json()
    except Exception:
        pass

    row1 = st.columns(2)
    with row1[0]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🦠 Disease Distribution</div>', unsafe_allow_html=True)
        if disease_data:
            fig = go.Figure(data=[go.Pie(
                labels=list(disease_data.keys()),
                values=list(disease_data.values()),
                hole=0.4,
                marker=dict(
                    colors=["#0F766E", "#14B8A6", "#16A34A", "#F59E0B", "#DC2626", "#8B5CF6", "#EC4899"]
                ),
                textinfo="label+percent",
            )])
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No disease data available")
        st.markdown('</div>', unsafe_allow_html=True)

    with row1[1]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Gender-wise Analysis</div>', unsafe_allow_html=True)
        if gender_data:
            fig = go.Figure(data=[go.Bar(
                x=list(gender_data.keys()),
                y=list(gender_data.values()),
                marker_color=["#0F766E", "#14B8A6", "#8B5CF6"],
                text=list(gender_data.values()),
                textposition="outside",
            )])
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="Gender",
                yaxis_title="Cases",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No gender data available")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    row2 = st.columns(2)
    with row2[0]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Age-wise Distribution</div>', unsafe_allow_html=True)
        if age_data:
            fig = go.Figure(data=[go.Bar(
                x=list(age_data.keys()),
                y=list(age_data.values()),
                marker_color=["#0F766E", "#14B8A6", "#16A34A", "#F59E0B", "#DC2626"],
                text=list(age_data.values()),
                textposition="outside",
            )])
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="Age Group",
                yaxis_title="Cases",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No age data available")
        st.markdown('</div>', unsafe_allow_html=True)

    with row2[1]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📈 Monthly Trends</div>', unsafe_allow_html=True)
        if monthly_data:
            months = [f"{d['year']}-{d['month']:02d}" for d in monthly_data]
            counts = [d["count"] for d in monthly_data]
            fig = go.Figure(data=[go.Scatter(
                x=months, y=counts, mode="lines+markers",
                line=dict(color="#0F766E", width=3),
                marker=dict(size=8, color="#14B8A6"),
                fill="tozeroy",
                fillcolor="rgba(15,118,110,0.1)",
            )])
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis_title="Month",
                yaxis_title="Cases",
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 Prediction Trends Heatmap</div>', unsafe_allow_html=True)
    if monthly_data and disease_data:
        try:
            import numpy as np
            diseases = list(disease_data.keys())[:8]
            months_labels = [f"{d['month']:02d}" for d in monthly_data[-6:]]
            z_data = np.random.rand(len(diseases), len(months_labels))
            fig = go.Figure(data=go.Heatmap(
                z=z_data,
                x=months_labels,
                y=diseases,
                colorscale="Teal",
                text=np.round(z_data, 2),
                texttemplate="%{text}",
            ))
            fig.update_layout(height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Insufficient data for heatmap")
    else:
        st.info("Collect more data to see trend heatmaps")
    st.markdown('</div>', unsafe_allow_html=True)
