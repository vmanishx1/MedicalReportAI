import streamlit as st


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:1rem 0;border-bottom:1px solid #E2E8F0;">
            <div style="font-size:2.5rem;margin-bottom:0.3rem;">🏥</div>
            <h3 style="color:#0F766E;margin:0;font-weight:700;">Medical Report AI</h3>
            <p style="color:#64748B;font-size:0.8rem;margin:0;">Chest X-Ray Analysis System</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        menu_items = [
            ("📊", "Dashboard"),
            ("📤", "Upload X-ray"),
            ("🔍", "Predictions"),
            ("📋", "Reports"),
            ("📁", "History"),
            ("📈", "Analytics"),
            ("⚙️", "Settings"),
        ]

        for icon, label in menu_items:
            if st.button(
                f"{icon} {label}",
                use_container_width=True,
                type="secondary" if st.session_state.page != label else "primary",
            ):
                st.session_state.page = label
                st.rerun()

        st.markdown("<br><br>", unsafe_allow_html=True)

        if st.session_state.authenticated:
            st.markdown(f"""
            <div style="padding:1rem;background:#F0FDFA;border-radius:12px;text-align:center;">
                <p style="color:#0F766E;font-weight:600;margin:0;font-size:0.85rem;">
                    👤 {st.session_state.username}
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("🚪 Logout", use_container_width=True, type="secondary"):
                st.session_state.authenticated = False
                st.session_state.token = None
                st.session_state.username = None
                st.session_state.page = "Dashboard"
                st.rerun()
