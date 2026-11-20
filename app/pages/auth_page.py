import streamlit as st
import requests as http_requests
from utils.config import config
from utils.logger import log

API_BASE = "http://localhost:8000"


def render_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 1.5rem 0;">
            <div style="font-size:4rem;">🏥</div>
            <h1 style="color:#0F766E;font-weight:700;margin:0.5rem 0;">Medical Report AI</h1>
            <p style="color:#64748B;font-size:1.1rem;">Chest X-Ray Analysis & Diagnostic Report System</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

        with tab1:
            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    remember = st.checkbox("Remember Me")
                with col_b:
                    st.markdown("<br>", unsafe_allow_html=True)

                if st.form_submit_button("Login", use_container_width=True, type="primary"):
                    if username and password:
                        try:
                            resp = http_requests.post(
                                f"{API_BASE}/api/auth/login",
                                json={"username": username, "password": password},
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.authenticated = True
                                st.session_state.token = data["access_token"]
                                st.session_state.username = data["username"]
                                st.success("Login successful!")
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                        except Exception as e:
                            st.error(f"Connection error: {e}. Please ensure the backend is running.")
                    else:
                        st.warning("Please enter username and password")

        with tab2:
            with st.form("signup_form"):
                new_user = st.text_input("Username", placeholder="Choose a username")
                new_email = st.text_input("Email", placeholder="your@email.com")
                new_name = st.text_input("Full Name", placeholder="Dr. John Doe")
                new_pass = st.text_input("Password", type="password", placeholder="Create a password")
                new_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm password")

                if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
                    if new_pass != new_confirm:
                        st.error("Passwords do not match")
                    elif new_user and new_email and new_pass:
                        try:
                            resp = http_requests.post(
                                f"{API_BASE}/api/auth/register",
                                json={
                                    "username": new_user,
                                    "email": new_email,
                                    "password": new_pass,
                                    "full_name": new_name,
                                },
                            )
                            if resp.status_code == 201:
                                data = resp.json()
                                st.session_state.authenticated = True
                                st.session_state.token = data["access_token"]
                                st.session_state.username = data["username"]
                                st.success("Account created! Welcome!")
                                st.rerun()
                            else:
                                st.error(resp.json().get("detail", "Registration failed"))
                        except Exception as e:
                            st.error(f"Connection error: {e}")
                    else:
                        st.warning("Please fill all required fields")
