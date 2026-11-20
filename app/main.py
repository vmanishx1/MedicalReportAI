import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from utils.config import config
from utils.logger import log

st.set_page_config(
    page_title="Medical Report AI - Chest X-Ray Analysis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

from app.components.sidebar import render_sidebar
from app.components.styles import load_custom_css
from app.pages.dashboard import render_dashboard
from app.pages.upload import render_upload_page
from app.pages.predictions import render_predictions_page
from app.pages.reports_page import render_reports_page
from app.pages.history import render_history_page
from app.pages.analytics import render_analytics_page
from app.pages.settings import render_settings_page
from app.pages.auth_page import render_auth_page


def initialize_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "token" not in st.session_state:
        st.session_state.token = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    if "prediction_result" not in st.session_state:
        st.session_state.prediction_result = None
    if "reports" not in st.session_state:
        st.session_state.reports = []


def main():
    initialize_session_state()
    load_custom_css()

    if not st.session_state.authenticated:
        render_auth_page()
        return

    render_sidebar()

    page_routes = {
        "Dashboard": render_dashboard,
        "Upload X-ray": render_upload_page,
        "Predictions": render_predictions_page,
        "Reports": render_reports_page,
        "History": render_history_page,
        "Analytics": render_analytics_page,
        "Settings": render_settings_page,
    }

    page = st.session_state.page
    if page in page_routes:
        page_routes[page]()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
