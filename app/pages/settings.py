import streamlit as st


def render_settings_page():
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Settings</h1>
        <p>Configure application preferences</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Profile Settings</div>', unsafe_allow_html=True)
        with st.form("profile_form"):
            st.text_input("Full Name", value=st.session_state.get("username", ""), disabled=True)
            st.text_input("Email", value="doctor@hospital.com")
            st.text_input("Hospital", value="City General Hospital")
            st.text_input("Specialization", value="Radiology")
            st.form_submit_button("💾 Update Profile", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔐 Security</div>', unsafe_allow_html=True)
        with st.form("password_form"):
            st.text_input("Current Password", type="password")
            st.text_input("New Password", type="password")
            st.text_input("Confirm New Password", type="password")
            st.form_submit_button("🔄 Change Password", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎨 Appearance</div>', unsafe_allow_html=True)
        theme = st.selectbox("Theme", ["Light Mode", "Dark Mode"])
        language = st.selectbox("Language", ["English", "Spanish", "French", "German"])
        st.markdown('<div class="section-title">🔬 Model Settings</div>', unsafe_allow_html=True)
        st.selectbox("Default Model", ["Auto (Best)", "DenseNet121", "EfficientNet-B3", "ResNet50", "ViT"])
        st.slider("Confidence Threshold", 0.1, 0.9, 0.3, 0.05)
        st.markdown('<div class="section-title">📄 Report Settings</div>', unsafe_allow_html=True)
        st.checkbox("Include Grad-CAM in reports", value=True)
        st.checkbox("Auto-generate PDF after analysis", value=False)
        st.checkbox("Include confidence scores", value=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">ℹ️ About</div>', unsafe_allow_html=True)
    st.markdown("""
    <table style="width:100%;">
        <tr><td><strong>Application</strong></td><td>Medical Report AI v2.0</td></tr>
        <tr><td><strong>Developer</strong></td><td>Medical AI Research Lab</td></tr>
        <tr><td><strong>Framework</strong></td><td>FastAPI + Streamlit + PyTorch</td></tr>
        <tr><td><strong>Models</strong></td><td>EfficientNet-B3, ResNet50, DenseNet121, ViT</td></tr>
        <tr><td><strong>Database</strong></td><td>SQLite (PostgreSQL ready)</td></tr>
        <tr><td><strong>Last Updated</strong></td><td>July 2026</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
