import streamlit as st


def load_custom_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        * { font-family: 'Inter', sans-serif; }

        .stApp {
            background-color: #F8FAFC;
        }

        .main-header {
            background: linear-gradient(135deg, #0F766E 0%, #14B8A6 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(15, 118, 110, 0.2);
        }

        .main-header h1 {
            color: white !important;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }

        .main-header p {
            color: rgba(255,255,255,0.85);
            font-size: 1rem;
            margin: 0.3rem 0 0 0;
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.06);
            border: 1px solid #E2E8F0;
            transition: all 0.2s ease;
        }

        .card:hover {
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }

        .metric-card {
            background: white;
            border-radius: 16px;
            padding: 1.2rem;
            text-align: center;
            border-left: 4px solid #0F766E;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        }

        .metric-card .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #0F766E;
        }

        .metric-card .metric-label {
            font-size: 0.85rem;
            color: #64748B;
            margin-top: 0.3rem;
        }

        .metric-card.danger { border-left-color: #DC2626; }
        .metric-card.danger .metric-value { color: #DC2626; }
        .metric-card.warning { border-left-color: #F59E0B; }
        .metric-card.warning .metric-value { color: #F59E0B; }
        .metric-card.success { border-left-color: #16A34A; }
        .metric-card.success .metric-value { color: #16A34A; }

        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #0F766E;
            margin: 1.5rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #14B8A6;
        }

        .badge {
            display: inline-block;
            padding: 0.2rem 0.7rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-success { background: #DCFCE7; color: #16A34A; }
        .badge-warning { background: #FEF3C7; color: #D97706; }
        .badge-danger { background: #FEE2E2; color: #DC2626; }
        .badge-info { background: #DBEAFE; color: #2563EB; }

        .gradcam-container {
            border: 2px solid #14B8A6;
            border-radius: 16px;
            padding: 0.8rem;
            background: white;
        }

        .prediction-item {
            background: #F8FAFC;
            border-radius: 12px;
            padding: 0.8rem 1rem;
            margin: 0.5rem 0;
            border-left: 4px solid #0F766E;
        }

        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(15, 118, 110, 0.3);
        }

        .upload-area {
            border: 2px dashed #14B8A6;
            border-radius: 16px;
            padding: 3rem;
            text-align: center;
            background: #F0FDFA;
            transition: all 0.3s;
        }

        .upload-area:hover {
            border-color: #0F766E;
            background: #CCFBF1;
        }

        .report-card {
            background: white;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            border: 1px solid #E2E8F0;
        }

        @media (prefers-color-scheme: dark) {
            .stApp { background-color: #0F172A; }
            .card { background: #1E293B; border-color: #334155; }
            .metric-card { background: #1E293B; }
            .section-title { color: #5EEAD4; }
        }
    </style>
    """, unsafe_allow_html=True)
