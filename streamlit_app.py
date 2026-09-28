
import os
import html

import pandas as pd
import uuid 
import plotly.graph_objects as go
import requests
import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# APPLICATION SETTINGS
# ============================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8001",
)


# ============================================================
# SESSION STATE
# ============================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = None

if "username" not in st.session_state:
    st.session_state.username = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "uploaded_dataset" not in st.session_state:
    st.session_state.uploaded_dataset = None

if "uploaded_dataset_name" not in st.session_state:
    st.session_state.uploaded_dataset_name = None

if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

if "preview_dataset" not in st.session_state:
    st.session_state.preview_dataset = False

if "selected_question" not in st.session_state:
    st.session_state.selected_question = ""

cookies = EncryptedCookieManager(
    prefix="ai-data-analyst/",
    password=os.getenv(
        "COOKIES_PASSWORD",
        "ai-data-analyst-local-secret",
    ),

)

if not cookies.ready():
    st.stop()


if not st.session_state.access_token:
    st.session_state.access_token = cookies.get("access_token")

if not st.session_state.username:
    st.session_state.username = cookies.get("username")


# ============================================================
# HTML RENDER HELPER
# ============================================================

def render_html(markup: str):
    st.html(markup.strip())


# ============================================================
# CUSTOM CSS
# ============================================================

st.html(
    """
    <style>

    /* ========================================================
       STREAMLIT CHROME
       ======================================================== */

 header {
    background: transparent !important;
    height: auto !important;
    min-height: 2.5rem !important;
    visibility: visible !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    height: auto !important;
    min-height: 2.5rem !important;
    visibility: visible !important;
    z-index: 999999 !important;
}

[data-testid="stHeader"] button {
    visibility: visible !important;
    opacity: 1 !important;
}

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stAppDeployButton"] {
        display: none !important;
    }

    #MainMenu {
        display: none !important;
    }

    footer {
        display: none !important;
    }


    /* ========================================================
       GLOBAL APP
       ======================================================== */

    .stApp {
        min-height: 100vh;

        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(120, 37, 255, 0.34),
                transparent 22%
            ),
            radial-gradient(
                circle at 97% 3%,
                rgba(39, 76, 255, 0.27),
                transparent 24%
            ),
            radial-gradient(
                circle at 5% 96%,
                rgba(28, 54, 150, 0.25),
                transparent 25%
            ),
            radial-gradient(
                circle at 96% 96%,
                rgba(150, 35, 255, 0.27),
                transparent 24%
            ),
            #071026;
    }

    .main {
        padding-top: 0 !important;
    }

    .block-container {
        max-width: 1180px !important;
        padding-top: 0.65rem !important;
        padding-bottom: 2rem !important;
    }


    /* ========================================================
       BACKGROUND ORBS
       ======================================================== */

    .stApp::before {
        content: "";

        position: fixed;

        width: 430px;
        height: 300px;

        left: -260px;
        top: -100px;

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse,
                rgba(137, 48, 255, 0.34),
                transparent 70%
            );

        pointer-events: none;
        z-index: 0;
    }

    .stApp::after {
        content: "";

        position: fixed;

        width: 500px;
        height: 340px;

        right: -280px;
        bottom: -130px;

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse,
                rgba(111, 38, 255, 0.30),
                transparent 70%
            );

        pointer-events: none;
        z-index: 0;
    }


    /* ========================================================
       BRAND
       ======================================================== */

    .brand-row {
        display: flex;
        align-items: center;

        gap: 10px;

        margin-top: 0.15rem;

        position: relative;
        z-index: 5;
    }

    .brand-icon {
        width: 42px;
        height: 42px;

        border-radius: 10px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 20px;

        background:
            linear-gradient(
                145deg,
                #26d8b0,
                #387cff 52%,
                #9d36ff
            );

        box-shadow:
            0 0 28px rgba(95, 84, 255, 0.42);
    }

    .brand-name {
        background:
            linear-gradient(
                90deg,
                #37a8ff,
                #8064ff,
                #dc3cff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;

        color: #f5f7ff;

        font-size: 1.28rem;

        font-weight: 850;

        letter-spacing: -0.035em;

        line-height: 1.1;
    }

    .brand-description {
        color: rgba(221, 228, 250, 0.56);

        font-size: 0.67rem;

        margin-top: 3px;
    }


    /* ========================================================
       AUTH PAGE
       ======================================================== */

    .auth-page {
        width: 100%;

        position: relative;

        z-index: 2;
    }

    /* ========================================================
   AUTH COLUMN SIZE ALIGNMENT
   KEEP BOTH SIDES EQUAL
   ======================================================== */

[data-testid="stHorizontalBlock"] {
    align-items: stretch !important;
    width: 100% !important;
}

[data-testid="stHorizontalBlock"] > [data-testid="column"] {
    width: 50% !important;
    min-width: 50% !important;
    flex: 0 0 50% !important;
    align-self: stretch !important;
}

[data-testid="stHorizontalBlock"] > [data-testid="column"] > div {
    width: 100% !important;
    height: 100% !important;
}


    /* ========================================================
       COMPLETE AUTH OUTER BOX
       WELCOME + LOGIN/SIGNUP + RIGHT VISUAL PANEL
       ======================================================== */

    [data-testid="stHorizontalBlock"]:has(.st-key-auth-left-panel) {
        min-height: 500px !important;
        height: 500px !important;
        box-sizing: border-box !important;

        border: 1px solid rgba(111, 96, 190, 0.38) !important;
        border-radius: 14px !important;

        background:
            linear-gradient(
                145deg,
                rgba(13, 25, 58, 0.30),
                rgba(8, 17, 42, 0.34)
            ) !important;

        box-shadow:
            0 20px 55px rgba(0, 0, 0, 0.18) !important;

        overflow: hidden !important;
    }

    .st-key-auth-left-panel {
        min-height: 500px !important;
        height: 500px !important;
        box-sizing: border-box !important;

        padding: 1.05rem !important;

        border: none !important;
        border-radius: 0 !important;

        background: transparent !important;

        box-shadow: none !important;
    }

    /* ========================================================
       WELCOME SECTION
       ======================================================== */

    .welcome-title {
        text-align: center;

        margin-top: 1.2rem;
        margin-bottom: 0.25rem;

        font-size: 2.15rem;

        line-height: 1.08;

        font-weight: 850;

        letter-spacing: -0.05em;

        background:
            linear-gradient(
                90deg,
                #299eff,
                #7b62ff,
                #d13bff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .welcome-description {
        text-align: center;

        color: rgba(224, 231, 252, 0.66);

        font-size: 0.78rem;

        margin-bottom: 1.2rem;
    }


    /* ========================================================
       LOGIN / SIGNUP CARD
       ======================================================== */

    .login-wrapper {
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: rgba(111, 96, 190, 0.38) !important;

        background:
            linear-gradient(
                145deg,
                rgba(13, 25, 58, 0.72),
                rgba(8, 17, 42, 0.74)
            ) !important;

        border-radius: 14px !important;

        box-shadow:
            0 20px 55px rgba(0, 0, 0, 0.22);
    }


/* ========================================================
   TABS
   ======================================================== */

[data-baseweb="tab-list"] {
    background: transparent !important;

    border-bottom:
        1px solid
        rgba(142, 149, 199, 0.18) !important;

    gap: 0 !important;
}


/* ========================================================
   TAB BUTTON
   ======================================================== */

button[data-baseweb="tab"],
[data-baseweb="tab"] {

    flex: 1 !important;

    justify-content: center !important;

    color:
        rgba(224, 231, 252, 0.68) !important;

    font-size: 0.78rem !important;

    font-weight: 650 !important;

    padding-top: 0.45rem !important;
    padding-bottom: 0.68rem !important;

    background: transparent !important;

    border: 0 !important;

    border-top: 0 !important;
    border-right: 0 !important;
    border-bottom: 0 !important;
    border-left: 0 !important;

    outline: none !important;

    box-shadow: none !important;

    text-decoration: none !important;
}


/* ========================================================
   REMOVE RED BORDER / FOCUS RING
   ======================================================== */

button[data-baseweb="tab"]:hover,
button[data-baseweb="tab"]:focus,
button[data-baseweb="tab"]:focus-visible,
button[data-baseweb="tab"]:active,
[data-baseweb="tab"]:hover,
[data-baseweb="tab"]:focus,
[data-baseweb="tab"]:focus-visible,
[data-baseweb="tab"]:active {

    background: transparent !important;

    border: 0 !important;

    border-top: 0 !important;
    border-right: 0 !important;
    border-bottom: 0 !important;
    border-left: 0 !important;

    outline: none !important;

    box-shadow: none !important;
}


/* ========================================================
   REMOVE RED FROM INNER TAB ELEMENTS
   ======================================================== */

button[data-baseweb="tab"] *,
[data-baseweb="tab"] * {

    border-color: transparent !important;

    outline: none !important;

    box-shadow: none !important;
}


/* ========================================================
   NORMAL TAB TEXT
   ======================================================== */

button[data-baseweb="tab"] span,
button[data-baseweb="tab"] p,
[data-baseweb="tab"] span,
[data-baseweb="tab"] p {

    color:
        rgba(224, 231, 252, 0.68) !important;

    -webkit-text-fill-color:
        rgba(224, 231, 252, 0.68) !important;

    background: transparent !important;

    text-decoration: none !important;
}


/* ========================================================
   HOVER TAB TEXT
   BLUE → PURPLE → PINK
   ======================================================== */

button[data-baseweb="tab"]:hover span,
button[data-baseweb="tab"]:hover p,
[data-baseweb="tab"]:hover span,
[data-baseweb="tab"]:hover p {

    color: transparent !important;

    background:
        linear-gradient(
            90deg,
            #299eff 0%,
            #7b62ff 48%,
            #d13bff 100%
        ) !important;

    background-clip: text !important;

    -webkit-background-clip: text !important;

    -webkit-text-fill-color: transparent !important;
}


/* ========================================================
   SELECTED TAB
   ======================================================== */

button[data-baseweb="tab"][aria-selected="true"],
[data-baseweb="tab"][aria-selected="true"] {

    color: transparent !important;

    background: transparent !important;

    border: 0 !important;

    border-top: 0 !important;
    border-right: 0 !important;
    border-bottom: 0 !important;
    border-left: 0 !important;

    outline: none !important;

    box-shadow: none !important;
}


/* ========================================================
   SELECTED TAB TEXT
   ======================================================== */

button[data-baseweb="tab"][aria-selected="true"] span,
button[data-baseweb="tab"][aria-selected="true"] p,
[data-baseweb="tab"][aria-selected="true"] span,
[data-baseweb="tab"][aria-selected="true"] p {

    color: transparent !important;

    background:
        linear-gradient(
            90deg,
            #299eff 0%,
            #7b62ff 48%,
            #d13bff 100%
        ) !important;

    background-clip: text !important;

    -webkit-background-clip: text !important;

    -webkit-text-fill-color: transparent !important;

    font-weight: 750 !important;
}


/* ========================================================
   SELECTED TAB HOVER
   KEEP GRADIENT — NEVER RED
   ======================================================== */

button[data-baseweb="tab"][aria-selected="true"]:hover,
button[data-baseweb="tab"][aria-selected="true"]:focus,
button[data-baseweb="tab"][aria-selected="true"]:focus-visible,
button[data-baseweb="tab"][aria-selected="true"]:active,
[data-baseweb="tab"][aria-selected="true"]:hover,
[data-baseweb="tab"][aria-selected="true"]:focus,
[data-baseweb="tab"][aria-selected="true"]:focus-visible,
[data-baseweb="tab"][aria-selected="true"]:active {

    color: transparent !important;

    background: transparent !important;

    border: 0 !important;

    border-top: 0 !important;
    border-right: 0 !important;
    border-bottom: 0 !important;
    border-left: 0 !important;

    outline: none !important;

    box-shadow: none !important;
}


/* ========================================================
   REMOVE STREAMLIT TAB PSEUDO ELEMENTS
   ======================================================== */

button[data-baseweb="tab"]::before,
button[data-baseweb="tab"]::after,
[data-baseweb="tab"]::before,
[data-baseweb="tab"]::after {

    content: none !important;

    display: none !important;

    border: none !important;

    background: transparent !important;

    box-shadow: none !important;
}


/* ========================================================
   TAB HIGHLIGHT / UNDERLINE
   ONLY THIS REMAINS VISIBLE
   ======================================================== */

[data-baseweb="tab-highlight"] {

    background:
        linear-gradient(
            90deg,
            #299eff 0%,
            #7b62ff 48%,
            #d13bff 100%
        ) !important;

    height: 3px !important;

    border: none !important;

    border-radius: 999px !important;

    box-shadow: none !important;
}


/* ========================================================
   TAB BORDER
   ======================================================== */

[data-baseweb="tab-border"] {

    background:
        rgba(142, 149, 199, 0.18) !important;

    border: none !important;

    box-shadow: none !important;
}


    /* ========================================================
       LOGIN CONTENT
       ======================================================== */

    .login-card-title {
        color: #f4f7ff;

        font-size: 1.05rem;

        font-weight: 750;

        margin-top: 0.75rem;

        margin-bottom: 0.12rem;
    }

    .login-card-description {
        color:
            rgba(221, 228, 250, 0.55);

        font-size: 0.68rem;

        margin-bottom: 0.65rem;
    }


    /* ========================================================
       INPUTS
       ======================================================== */

    .stTextInput label {
        color: #eaf0ff !important;

        font-size: 0.73rem !important;

        font-weight: 600 !important;
    }

    .stTextInput input {
        height: 40px !important;

        background:
            rgba(25, 36, 70, 0.86) !important;

        color: #f1f5ff !important;

        border:
            1px solid
            rgba(116, 130, 180, 0.30) !important;

        border-radius: 8px !important;

        font-size: 0.74rem !important;
    }

    .stTextInput input:focus {
        border-color:
            rgba(118, 93, 255, 0.82) !important;

        box-shadow:
            0 0 0 1px
            rgba(118, 93, 255, 0.22) !important;
    }


    /* ========================================================
       LOGIN + CREATE ACCOUNT BUTTONS
       ======================================================== */

    [data-testid="stFormSubmitButton"] button,
    [data-testid="stFormSubmitButton"] button[kind="primary"] {

        min-height: 40px !important;

        border: none !important;

        border-radius: 9px !important;

        background:
            linear-gradient(
                90deg,
                #258fff 0%,
                #675dff 48%,
                #c735ff 100%
            ) !important;

        background-color: transparent !important;

        color: #ffffff !important;

        -webkit-text-fill-color: #ffffff !important;

        font-size: 0.78rem !important;

        font-weight: 750 !important;

        box-shadow:
            0 9px 25px
            rgba(105, 57, 255, 0.28) !important;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease !important;
    }


    /* ========================================================
       FORM BUTTON HOVER
       ======================================================== */

    [data-testid="stFormSubmitButton"] button:hover,
    [data-testid="stFormSubmitButton"] button:focus,
    [data-testid="stFormSubmitButton"] button:active,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:hover,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:focus,
    [data-testid="stFormSubmitButton"] button[kind="primary"]:active {

        background:
            linear-gradient(
                90deg,
                #258fff 0%,
                #675dff 48%,
                #c735ff 100%
            ) !important;

        background-color: transparent !important;

        color: #ffffff !important;

        -webkit-text-fill-color: #ffffff !important;

        border: none !important;

        box-shadow:
            0 13px 30px
            rgba(105, 57, 255, 0.40) !important;

        transform: translateY(-1px) !important;
    }


    /* ========================================================
       LOGIN INFO
       ======================================================== */

    .login-info {
        margin-top: 0.72rem;

        padding: 0.72rem 0.78rem;

        border-radius: 9px;

        border:
            1px solid
            rgba(53, 103, 255, 0.55);

        background:
            linear-gradient(
                135deg,
                rgba(19, 58, 130, 0.48),
                rgba(29, 36, 107, 0.34)
            );

        color:
            rgba(225, 234, 255, 0.70);

        font-size: 0.64rem;

        line-height: 1.45;
    }

    .login-info strong {
        color: #e9edff;
    }


    /* ========================================================
       RIGHT VISUAL PANEL
       ======================================================== */

   .visual-panel {
    min-height: 500px;
    height: 100%;
    box-sizing: border-box;

    padding:
        1.35rem
        1.15rem
        1.1rem
        1.15rem;

    position: relative;

    overflow: hidden;
}

    .visual-panel::before {
        content: "";

        position: absolute;

        width: 300px;
        height: 300px;

        right: -110px;
        top: -120px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(67, 71, 255, 0.23),
                transparent 68%
            );
    }

    .visual-panel::after {
        content: "";

        position: absolute;

        width: 270px;
        height: 270px;

        left: -130px;
        bottom: -150px;

        border-radius: 50%;

        background:
            radial-gradient(
                circle,
                rgba(157, 39, 255, 0.24),
                transparent 68%
            );
    }


    /* ========================================================
       POWERED BY AI BADGE
       ======================================================== */

    .powered-badge {
        position: relative;

        z-index: 4;

        display: inline-flex;

        align-items: center;

        gap: 7px;

        padding:
            0.38rem
            0.72rem;

        border-radius: 999px;

        border:
            1px solid
            rgba(65, 126, 255, 0.48);

        background:
            linear-gradient(
                90deg,
                rgba(27, 73, 165, 0.30),
                rgba(91, 42, 176, 0.25)
            );

        color:
            rgba(220, 231, 255, 0.82);

        font-size: 0.58rem;

        font-weight: 700;

        letter-spacing: 0.04em;

        box-shadow:
            0 0 22px
            rgba(72, 76, 255, 0.16);
    }

    .powered-star {
        color: #ffffff;

        font-size: 11px;
    }


    /* ========================================================
       VISUAL HEADLINE
       ======================================================== */

    .visual-title {
        position: relative;

        z-index: 3;

        font-size: 1.95rem;

        line-height: 1.02;

        font-weight: 850;

        letter-spacing: -0.045em;

        color: #f5f7ff;

        margin-top: 0.85rem;

        margin-bottom: 0.65rem;
    }

    .visual-title .gradient-text {
        background:
            linear-gradient(
                90deg,
                #37a8ff,
                #a05cff,
                #e83dff
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .visual-description {
        position: relative;

        z-index: 3;

        color:
            rgba(220, 228, 252, 0.62);

        font-size: 0.70rem;

        line-height: 1.55;

        max-width: 480px;

        margin-bottom: 1rem;
    }


    /* ========================================================
       MINI VISUAL GRID
       ======================================================== */

    .visual-grid {
        position: relative;

        z-index: 3;

        display: grid;

        grid-template-columns:
            0.95fr
            1.15fr;

        gap: 0.65rem;

        align-items: start;
    }

    .visual-column {
        display: flex;

        flex-direction: column;

        gap: 0.65rem;
    }

    .visual-box {
        border-radius: 11px;

        border:
            1px solid
            rgba(129, 74, 255, 0.58);

        background:
            linear-gradient(
                145deg,
                rgba(26, 27, 68, 0.88),
                rgba(10, 25, 57, 0.82)
            );

        box-shadow:
            0 15px 35px
            rgba(0, 0, 0, 0.23),
            inset 0 1px 0
            rgba(255, 255, 255, 0.035);

        overflow: hidden;
    }


    /* ========================================================
       VISUAL BOX HEADER
       ======================================================== */

    .visual-box-header {
        display: flex;

        align-items: center;

        justify-content: space-between;

        padding:
            0.52rem
            0.62rem;

        border-bottom:
            1px solid
            rgba(150, 160, 210, 0.12);

        color: #f1f4ff;

        font-size: 0.64rem;

        font-weight: 700;
    }

    .visual-box-title {
        display: flex;

        align-items: center;

        gap: 6px;
    }

    .visual-icon {
        width: 20px;
        height: 20px;

        border-radius: 5px;

        display: flex;

        align-items: center;
        justify-content: center;

        background:
            linear-gradient(
                135deg,
                #6c45ff,
                #d934ff
            );

        font-size: 10px;

        box-shadow:
            0 0 14px
            rgba(173, 47, 255, 0.35);
    }

    .visual-dots {
        color:
            rgba(225, 230, 255, 0.55);

        letter-spacing: 2px;
    }


    /* ========================================================
       SQL VISUAL
       ======================================================== */

    .sql-content {
        padding: 0.65rem;

        font-family:
            Consolas,
            "Courier New",
            monospace;

        font-size: 0.54rem;

        line-height: 1.65;

        color: #b9c9f5;
    }

    .sql-keyword {
        color: #e25cff;
    }

    .sql-blue {
        color: #3eb6ff;
    }

    .sql-yellow {
        color: #ffc83d;
    }

    .sql-pink {
        color: #ff5bd7;
    }


    /* ========================================================
       CHART VISUAL
       ======================================================== */

    .chart-content {
        padding:
            0.62rem
            0.55rem
            0.5rem;
    }

    .chart-area {
        height: 145px;

        display: flex;

        align-items: flex-end;

        justify-content: space-around;

        gap: 7px;

        padding:
            0.6rem
            0.45rem
            0.35rem;

        border-radius: 7px;

        background:
            repeating-linear-gradient(
                to top,
                rgba(148, 156, 214, 0.08) 0px,
                rgba(148, 156, 214, 0.08) 1px,
                transparent 1px,
                transparent 30px
            );
    }

    .chart-bar {
        width: 13%;

        border-radius:
            4px 4px 2px 2px;

        background:
            linear-gradient(
                to top,
                #d83bff,
                #a85cff 43%,
                #32a8ff 100%
            );

        box-shadow:
            0 0 15px
            rgba(134, 64, 255, 0.34);
    }

    .bar-one {
        height: 88%;
    }

    .bar-two {
        height: 69%;
    }

    .bar-three {
        height: 62%;
    }

    .bar-four {
        height: 53%;
    }

    .bar-five {
        height: 44%;
    }

    .bar-six {
        height: 39%;
    }


    /* ========================================================
       TABLE VISUAL
       ======================================================== */

    .table-content {
        padding: 0.52rem;

        font-size: 0.51rem;
    }

    .table-row {
        display: grid;

        grid-template-columns:
            0.35fr
            1fr
            0.8fr
            0.8fr;

        padding:
            0.28rem
            0.25rem;

        border-bottom:
            1px solid
            rgba(147, 158, 211, 0.09);

        color:
            rgba(228, 234, 255, 0.67);
    }

    .table-row.header {
        color: #b7c8f7;

        font-weight: 700;
    }


    /* ========================================================
       DATABASE ILLUSTRATION
       ======================================================== */

    .database-area {
        min-height: 165px;

        display: flex;

        align-items: center;
        justify-content: center;

        position: relative;
    }

    .database-glow {
        position: absolute;

        width: 180px;
        height: 90px;

        border-radius: 50%;

        background:
            radial-gradient(
                ellipse,
                rgba(133, 40, 255, 0.30),
                transparent 68%
            );

        filter: blur(4px);
    }

    .database {
        position: relative;

        width: 95px;
        height: 95px;
    }

    .db-layer {
        position: absolute;

        left: 0;

        width: 95px;
        height: 34px;

        border-radius: 50%;

        border:
            1px solid
            rgba(65, 177, 255, 0.88);

        background:
            linear-gradient(
                180deg,
                #4935d8,
                #301c91
            );

        box-shadow:
            0 0 18px
            rgba(72, 99, 255, 0.55);
    }

    .db-layer::after {
        content: "";

        position: absolute;

        left: -1px;
        right: -1px;

        bottom: -17px;

        height: 34px;

        border-radius: 50%;

        border:
            1px solid
            rgba(190, 47, 255, 0.80);

        background:
            linear-gradient(
                180deg,
                #371ea7,
                #22136d
            );
    }

    .db-top {
        top: 18px;
        z-index: 3;
    }

    .db-middle {
        top: 42px;
        z-index: 2;
    }

    .db-bottom {
        top: 66px;
        z-index: 1;
    }


    /* ========================================================
       PIPELINE BADGE
       ======================================================== */

    .pipeline-badge {
        position: relative;

        z-index: 4;

        display: inline-flex;

        align-items: center;

        gap: 7px;

        margin-top: 0.65rem;

        padding:
            0.40rem
            0.68rem;

        border-radius: 999px;

        border:
            1px solid
            rgba(159, 67, 255, 0.68);

        background:
            linear-gradient(
                90deg,
                rgba(68, 35, 170, 0.48),
                rgba(137, 36, 173, 0.32)
            );

        color:
            rgba(231, 233, 255, 0.84);

        font-size: 0.55rem;

        box-shadow:
            0 0 20px
            rgba(113, 48, 255, 0.18);
    }

    .pipeline-dot {
        width: 17px;
        height: 17px;

        display: flex;

        align-items: center;
        justify-content: center;

        border-radius: 50%;

        background:
            linear-gradient(
                135deg,
                #7648ff,
                #d42fff
            );

        font-size: 9px;
    }


    /* ========================================================
       WORKSPACE
       ======================================================== */

    .workspace-header {
        margin-bottom: 1.5rem;
        text-align: center;
    }

    .workspace-title {
        color: #f5f7ff;

        font-size: 2rem;

        font-weight: 800;
    }

    .workspace-subtitle {
        color:
            rgba(221, 228, 250, 0.58);

        font-size: 2rem;

        font-weight: 800;
    }

    /* ========================================================
   AUTHENTICATED WORKSPACE GRADIENT HEADINGS
   LOGIN PAGE UNTOUCHED
   ======================================================== */

.workspace-title,
.workspace-question-title {
    background:
        linear-gradient(
            90deg,
            #299eff 0%,
            #7b62ff 48%,
            #d13bff 100%
        ) !important;

    -webkit-background-clip: text !important;
    background-clip: text !important;
    -webkit-text-fill-color: transparent !important;

    color: transparent !important;
}

/* ========================================================
   ANALYZE DATA BUTTON
   AUTHENTICATED WORKSPACE ONLY
   ======================================================== */

div.stButton > button[kind="primary"] {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    border: none !important;
    border-radius: 10px !important;

    font-weight: 750 !important;
    min-height: 46px !important;

    box-shadow:
        0 10px 28px
        rgba(105, 57, 255, 0.30) !important;
}

div.stButton > button[kind="primary"]:hover {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    transform: translateY(-1px) !important;

    box-shadow:
        0 14px 32px
        rgba(105, 57, 255, 0.45) !important;
}


    /* ========================================================
       ANALYSIS RESULT
       ======================================================== */

    .insight-box {
        padding: 1rem 1.1rem;

        border-radius: 12px;

        border:
            1px solid
            rgba(119, 76, 255, 0.48);

        background:
            linear-gradient(
                135deg,
                rgba(31, 36, 88, 0.78),
                rgba(20, 24, 64, 0.72)
            );

        color:
            rgba(235, 240, 255, 0.86);

        line-height: 1.6;

        box-shadow:
            0 15px 35px
            rgba(0, 0, 0, 0.18);
    }


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #0a1531,
                #091126
            ) !important;

        border-right:
            1px solid
            rgba(96, 74, 190, 0.24);
    }

/* ========================================================
   SIDEBAR CONTENT
   ======================================================== */

[data-testid="stSidebar"] > div:first-child {
    padding-top: 0.35rem !important;
}

[data-testid="stSidebarContent"] {
    padding-top: 0.25rem !important;
}


/* ========================================================
   SIDEBAR BRAND
   ======================================================== */

.sidebar-brand {
    padding: 0.15rem 0 0.2rem 0;
    margin-top: -3.5rem;
}

.sidebar-brand-title {
    font-size: 1.30rem;
    font-weight: 800;
    color: #f5f7ff;
    line-height: 1.25;
    
}

.sidebar-brand-subtitle {
    margin-top: 0.18rem;
    font-size: 0.75rem;
    color: rgba(221, 228, 250, 0.58);
}


/* ========================================================
   SIDEBAR DIVIDERS
   ======================================================== */

[data-testid="stSidebar"] hr {
    margin: 0.38rem 0 !important;
    border-color: rgba(119, 76, 255, 0.18) !important;
}


/* ========================================================
   SIDEBAR SECTION HEADINGS
   ======================================================== */

[data-testid="stSidebar"] h3 {
    margin-top: 0.05rem !important;
    margin-bottom: 0.28rem !important;

    font-size: 0.92rem !important;
    font-weight: 750 !important;

    background:
        linear-gradient(
            90deg,
            #ffffff 0%,
            #9b8cff 55%,
            #d13bff 100%
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}


/* ========================================================
   DATA SOURCE AREA
   ======================================================== */

[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    margin-bottom: 0.2rem !important;
}

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    padding: 0.55rem !important;

    border-radius: 10px !important;

    border:
        1px solid
        rgba(103, 121, 205, 0.48) !important;

    background:
        linear-gradient(
            135deg,
            rgba(35, 69, 135, 0.90),
            rgba(66, 50, 126, 0.90)
        ) !important;

    box-shadow:
        0 7px 18px
        rgba(20, 35, 90, 0.20) !important;   
}


/* ========================================================
   SIDEBAR CAPTIONS
   ======================================================== */

[data-testid="stSidebar"] .stCaption {
    margin-top: 0.1rem !important;
    margin-bottom: 0.2rem !important;

    color:
        rgba(221, 228, 250, 0.56) !important;

    font-size: 0.72rem !important;
}

   /* ========================================================
    FORCE SIDEBAR VISIBLE
    TEMPORARY ROOT-CAUSE TEST
   ======================================================== */

[data-testid="stSidebar"] {
    visibility: visible !important;
    opacity: 1 !important;
    display: block !important;
    transform: translateX(0) !important;
}


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 900px) {

        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }

        .visual-panel {
            min-height: 400px;
        }

        .st-key-auth-left-panel {
            min-height: 400px !important;
            height: 400px !important;
        }

        .visual-grid {
            grid-template-columns: 1fr;
        }

        .welcome-title {
            font-size: 1.9rem;
        }

        .visual-title {
            font-size: 1.7rem;
        }
    }

/* ========================================================
   SIDEBAR TOGGLE CONTROLS
   FINAL
   ======================================================== */


/* ========================================================
   OPEN SIDEBAR — CLOSE BUTTON <
   ======================================================== */

section[data-testid="stSidebar"]
[data-testid="stSidebarHeader"]
[data-testid="stSidebarCollapseButton"] {
    display: flex !important;

    visibility: visible !important;
    opacity: 1 !important;

    pointer-events: auto !important;

    position: absolute !important;

    top: 8px !important;
    right: 8px !important;

    z-index: 999999 !important;
}


section[data-testid="stSidebar"]
[data-testid="stSidebarHeader"]
[data-testid="stSidebarCollapseButton"]
button {
    display: flex !important;

    visibility: visible !important;
    opacity: 1 !important;

    pointer-events: auto !important;

    align-items: center !important;
    justify-content: center !important;

    width: 38px !important;
    height: 38px !important;

    padding: 0 !important;

    border-radius: 9px !important;

    background:
        linear-gradient(
            135deg,
            rgba(55, 52, 125, 0.96),
            rgba(82, 55, 145, 0.96)
        ) !important;

    border:
        1px solid
        rgba(139, 124, 255, 0.55) !important;

    color: #ffffff !important;

    box-shadow:
        0 8px 22px
        rgba(0, 0, 0, 0.24) !important;
}


/* Hide Streamlit's original icon */

section[data-testid="stSidebar"]
[data-testid="stSidebarHeader"]
[data-testid="stSidebarCollapseButton"]
button svg {
    display: none !important;
}


/* Our < icon */

section[data-testid="stSidebar"]
[data-testid="stSidebarHeader"]
[data-testid="stSidebarCollapseButton"]
button::before {
    content: "<" !important;

    display: block !important;

    color: #ffffff !important;

    font-size: 25px !important;

    line-height: 1 !important;

    font-weight: 600 !important;
}


/* ========================================================
   CLOSED SIDEBAR — OPEN BUTTON >
   ======================================================== */

[data-testid="stSidebarCollapsedControl"] {
    display: flex !important;

    visibility: visible !important;
    opacity: 1 !important;

    pointer-events: auto !important;

    position: fixed !important;

    top: 14px !important;
    left: 14px !important;

    z-index: 999999 !important;
}


[data-testid="stSidebarCollapsedControl"] button {
    display: flex !important;

    visibility: visible !important;
    opacity: 1 !important;

    pointer-events: auto !important;

    align-items: center !important;
    justify-content: center !important;

    width: 42px !important;
    height: 42px !important;

    padding: 0 !important;

    border-radius: 10px !important;

    background:
        linear-gradient(
            135deg,
            rgba(55, 52, 125, 0.96),
            rgba(82, 55, 145, 0.96)
        ) !important;

    border:
        1px solid
        rgba(139, 124, 255, 0.55) !important;

    color: #ffffff !important;

    box-shadow:
        0 8px 22px
        rgba(0, 0, 0, 0.24) !important;
}


/* Hide Streamlit original icon */

[data-testid="stSidebarCollapsedControl"]
button svg {
    display: none !important;
}


/* Our > icon */

[data-testid="stSidebarCollapsedControl"]
button::before {
    content: ">" !important;

    display: block !important;

    color: #ffffff !important;

    font-size: 27px !important;

    line-height: 1 !important;

    font-weight: 600 !important;
}


/* ========================================================
   HOVER
   ======================================================== */

section[data-testid="stSidebar"]
[data-testid="stSidebarCollapseButton"]
button:hover,

[data-testid="stSidebarCollapsedControl"]
button:hover {
    background:
        linear-gradient(
            135deg,
            #386fff,
            #a936ff
        ) !important;

    border-color:
        rgba(180, 160, 255, 0.85) !important;
}

/* ========================================================
   HIDE NATIVE STREAMLIT TOGGLE
   Keep only our custom toggle visible
   ======================================================== */

section[data-testid="stSidebar"]
[data-testid="stSidebarCollapseButton"]
button,

[data-testid="stSidebarCollapsedControl"]
button {
    visibility: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
}

.sidebar-compact-description {
    margin-top: -0.15rem !important;
    margin-bottom: 0.25rem !important;
    color: rgba(221, 228, 250, 0.58) !important;
    font-size: 0.75rem !important;
    line-height: 1.25 !important;
}

/* ============================================================
   WORKSPACE + SIDEBAR COLOR POLISH
   ============================================================ */

/* ------------------------------------------------------------
   UPLOAD AREA
   ------------------------------------------------------------ */

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background:
        linear-gradient(
            135deg,
            rgba(27, 73, 145, 0.78),
            rgba(43, 38, 105, 0.78)
        ) !important;

    border:
        1px solid
        rgba(82, 108, 220, 0.55) !important;

    box-shadow:
        0 8px 20px
        rgba(20, 40, 100, 0.18) !important;
}


/* ------------------------------------------------------------
   TRY ASKING BUTTONS ONLY
   ------------------------------------------------------------ */

[data-testid="stSidebar"] .st-key-example_0 button,
[data-testid="stSidebar"] .st-key-example_1 button,
[data-testid="stSidebar"] .st-key-example_2 button,
[data-testid="stSidebar"] .st-key-example_3 button,
[data-testid="stSidebar"] [class*="st-key-history_"] button,
[data-testid="stSidebar"] [class*="st-key-delete_history_"] button {
    background:
        linear-gradient(
            135deg,
            rgba(35, 69, 135, 0.90),
            rgba(66, 50, 126, 0.90)
        ) !important;

    border:
        1px solid
        rgba(103, 121, 205, 0.48) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    border-radius: 9px !important;

    box-shadow:
        0 7px 18px
        rgba(20, 35, 90, 0.20) !important;
}

[data-testid="stSidebar"] .st-key-example_0 button:hover,
[data-testid="stSidebar"] .st-key-example_1 button:hover,
[data-testid="stSidebar"] .st-key-example_2 button:hover,
[data-testid="stSidebar"] .st-key-example_3 button:hover,
[data-testid="stSidebar"] [class*="st-key-history_"] button:hover,
[data-testid="stSidebar"] [class*="st-key-delete_history_"] button:hover {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    border-color:
        rgba(180, 160, 255, 0.75) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    transform: translateY(-1px) !important;

    box-shadow:
        0 11px 25px
        rgba(105, 57, 255, 0.32) !important;
}


/* ------------------------------------------------------------
   ENTER YOUR QUESTION
   ------------------------------------------------------------ */

div[data-testid="stTextArea"] textarea {
    background:
        linear-gradient(
            135deg,
            rgba(27, 48, 96, 0.92),
            rgba(38, 32, 82, 0.92)
        ) !important;

    color: #f1f5ff !important;
    -webkit-text-fill-color: #f1f5ff !important;

    border:
        1px solid
        rgba(76, 112, 210, 0.52) !important;

    border-radius: 10px !important;

    box-shadow:
        0 8px 24px
        rgba(25, 40, 100, 0.16) !important;
}

div[data-testid="stTextArea"] textarea::placeholder {
    color:
        rgba(190, 202, 235, 0.62) !important;
}

div[data-testid="stTextArea"] textarea:focus {
    border:
        1px solid
        rgba(91, 119, 255, 0.85) !important;

    box-shadow:
        0 0 0 1px
        rgba(91, 119, 255, 0.22),
        0 10px 28px
        rgba(50, 70, 150, 0.18) !important;
}


/* ------------------------------------------------------------
   LOGOUT ONLY
   ------------------------------------------------------------ */

[data-testid="stSidebar"] .st-key-logout_button button {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    border:
        none !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    box-shadow:
        0 10px 28px
        rgba(105, 57, 255, 0.30) !important;
}

[data-testid="stSidebar"] .st-key-logout_button button:hover {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    transform: translateY(-1px) !important;

    box-shadow:
        0 14px 32px
        rgba(105, 57, 255, 0.45) !important;
}

/* ============================================================
   UPLOAD BOX — FINAL COLOR
   ============================================================ */

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"],
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] > div,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] section {
    background:
        linear-gradient(
            135deg,
            #234585 0%,
            #42327e 100%
        ) !important;

    border:
        1px solid
        rgba(103, 121, 205, 0.65) !important;

    border-radius: 10px !important;

    box-shadow:
        0 7px 18px
        rgba(20, 35, 90, 0.22) !important;
}


/* Upload button itself */

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
    background:
        linear-gradient(
            135deg,
            #315ca8,
            #51419a
        ) !important;

    border:
        1px solid
        rgba(160, 170, 230, 0.45) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}


/* Upload button hover */

[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button:hover {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

/* ============================================================
   CLEAN UPLOAD INSTRUCTIONS
   ============================================================ */

/* Hide Streamlit's native instruction text */
[data-testid="stSidebar"]
[data-testid="stFileUploaderDropzoneInstructions"] {
    display: none !important;
}


/* Re-create the instruction text cleanly */
[data-testid="stSidebar"]
[data-testid="stFileUploaderDropzone"]::after {
    content: "200MB per file • CSV, XLSX, XLS";

    display: block !important;

    margin-top: 6px !important;

    text-align: center !important;

    font-size: 0.75rem !important;
    line-height: 1.2 !important;

    color: rgba(220, 228, 250, 0.68) !important;

    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;

    border-radius: 0 !important;
}

/* ------------------------------------------------------------
   PREVIEW DATA BUTTON
   Same style as Try Asking buttons
   ------------------------------------------------------------ */

[data-testid="stSidebar"] .st-key-preview_dataset_button button {
    background:
        linear-gradient(
            135deg,
            rgba(35, 69, 135, 0.90),
            rgba(66, 50, 126, 0.90)
        ) !important;

    border:
        1px solid
        rgba(103, 121, 205, 0.48) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    border-radius: 9px !important;

    box-shadow:
        0 7px 18px
        rgba(20, 35, 90, 0.20) !important;
}

[data-testid="stSidebar"] .st-key-preview_dataset_button button:hover {
    background:
        linear-gradient(
            90deg,
            #168fff 0%,
            #675dff 48%,
            #d13bff 100%
        ) !important;

    border-color:
        rgba(180, 160, 255, 0.75) !important;

    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;

    transform: translateY(-1px) !important;

    box-shadow:
        0 11px 25px
        rgba(105, 57, 255, 0.32) !important;
}
    </style>
    """
)


# ============================================================
# AUTHENTICATION HELPERS
# ============================================================

def login_user(username: str, password: str):

    payload = {
        "username": username.strip(),
        "password": password,
    }

    try:

        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.access_token = data["access_token"]

            st.session_state.username = data["username"]

            cookies["access_token"] = data["access_token"]
            cookies["username"] = data["username"]
            cookies.save()

            st.session_state.analysis_result = None

            return True

        try:

            error_data = response.json()

            error_message = error_data.get(
                "detail",
                "Login failed.",
            )

        except Exception:

            error_message = "Login failed."

        st.error(error_message)

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to FastAPI. "
            "Make sure the backend is running on port 8001."
        )

    except requests.exceptions.Timeout:

        st.error(
            "Login request timed out. Please try again."
        )

    except Exception as exc:

        st.error(
            f"Unexpected login error: {exc}"
        )

    return False


def signup_user(
    username: str,
    email: str,
    password: str,
):

    payload = {
        "username": username.strip(),
        "email": email.strip(),
        "password": password,
    }

    try:

        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=payload,
            timeout=30,
        )

        if response.status_code == 200:

            return True, "Account created successfully."

        try:

            error_data = response.json()

            error_message = error_data.get(
                "detail",
                "Signup failed.",
            )

        except Exception:

            error_message = "Signup failed."

        return False, error_message

    except requests.exceptions.ConnectionError:

        return (
            False,
            "Could not connect to FastAPI. "
            "Make sure the backend is running on port 8001.",
        )

    except requests.exceptions.Timeout:

        return (
            False,
            "Signup request timed out. Please try again.",
        )

    except Exception as exc:

        return (
            False,
            f"Unexpected signup error: {exc}",
        )


# ============================================================
# ANALYSIS REQUEST
# ============================================================

def run_analysis(question: str):

    if not st.session_state.access_token:

        st.error(
            "Please log in before running an analysis."
        )

        return None

    if st.session_state.uploaded_dataset is None:

        st.error(
            "Please upload a dataset before running an analysis."
        )

        return None

    headers = {
        "Authorization": (
            f"Bearer {st.session_state.access_token}"
        )
    }

    try:

        # ----------------------------------------------------
        # UPLOAD CURRENT DATASET TO BACKEND
        # ----------------------------------------------------

        uploaded_df = (
            st.session_state.uploaded_dataset
        )

        original_name = (
            st.session_state.uploaded_dataset_name
        )

        unique_name = (
            f"{original_name.rsplit('.', 1)[0]}"
            f"_{uuid.uuid4().hex[:8]}.csv"
        )

        csv_data = uploaded_df.to_csv(
            index=False
        ).encode("utf-8")

        files = {
            "file": (
                unique_name,
                csv_data,
                "text/csv",
            )
        }

        upload_response = requests.post(
            f"{API_BASE_URL}/api/datasets/upload",
            files=files,
            headers=headers,
            timeout=120,
        )

        if upload_response.status_code != 200:

            try:

                error_data = upload_response.json()

                error_message = error_data.get(
                    "detail",
                    "Dataset upload failed.",
                )

            except Exception:

                error_message = (
                    "Dataset upload failed."
                )

            st.error(
                f"Dataset upload failed: "
                f"{error_message}"
            )

            return None

        upload_data = upload_response.json()

        table_name = upload_data.get(
            "dataset",
            {}
        ).get(
            "table_name"
        )

        if not table_name:

            st.error(
                "Backend did not return a dataset table name."
            )

            return None

        # ----------------------------------------------------
        # ANALYSIS REQUEST
        # ----------------------------------------------------

        payload = {
            "question": question,
            "table_name": table_name,
        }

        response = requests.post(
            f"{API_BASE_URL}/api/analysis/query",
            json=payload,
            headers=headers,
            timeout=120,
        )

        if response.status_code == 200:

            return response.json()

        try:

            error_data = response.json()

            error_message = error_data.get(
                "detail",
                "Analysis request failed.",
            )

        except Exception:

            error_message = (
                "Analysis request failed."
            )

        st.error(
            f"Analysis failed: {error_message}"
        )

    except requests.exceptions.ConnectionError:

        st.error(
            "Could not connect to the FastAPI server. "
            "Make sure the backend is running on port 8001."
        )

    except requests.exceptions.Timeout:

        st.error(
            "The analysis request timed out. "
            "Please try again."
        )

    except Exception as exc:

        st.error(
            f"Unexpected error: {exc}"
        )

    return None


# ============================================================
# LOGIN PAGE
# ============================================================

if not st.session_state.access_token:

    # ========================================================
    # BRAND
    # ========================================================

    render_html(
        """
        <div class="brand-row">

            <div class="brand-icon">
                📊
            </div>

            <div>

                <div class="brand-name">
                    AI Data Analyst
                </div>

                <div class="brand-description">
                    Turn data questions into SQL, insights, and visualizations.
                </div>

            </div>

        </div>
        """
    )


    # ========================================================
    # TWO-COLUMN AUTH LAYOUT
    # ========================================================

    left_column, right_column = st.columns(
        [1, 1],
        gap="small",
    )


    # ========================================================
    # LEFT SIDE — LOGIN / SIGNUP
    # ========================================================

    with left_column:

        with st.container(border=True, key="auth-left-panel"):

            with st.container(border=True):

                render_html(
                    """
                    <div class="welcome-title">
                        Welcome 
                    </div>

                    <div class="welcome-description">
                        Log in to access your AI data analysis workspace.
                    </div>
                    """
                )

                login_tab, signup_tab = st.tabs(
                    [
                        "🔐  Login",
                        "✨  Create Account",
                    ]
                )


                # =================================================
                # LOGIN TAB
                # =================================================

                with login_tab:

                    render_html(
                        """
                        <div class="login-card-title">
                            Login to your account
                        </div>

                        <div class="login-card-description">
                            Enter your credentials to continue.
                        </div>
                        """
                    )

                    with st.form("login_form"):

                        login_username = st.text_input(
                            "Username",
                            placeholder="Enter your username",
                        )

                        login_password = st.text_input(
                            "Password",
                            type="password",
                            placeholder="Enter your password",
                        )

                        login_submitted = st.form_submit_button(
                            "Login  →",
                            type="primary",
                            use_container_width=True,
                        )

                    if login_submitted:

                        if not login_username.strip():

                            st.warning(
                                "Please enter your username."
                            )

                        elif not login_password:

                            st.warning(
                                "Please enter your password."
                            )

                        else:

                            with st.spinner(
                                "Signing you in..."
                            ):

                                logged_in = login_user(
                                    login_username,
                                    login_password,
                                )

                            if logged_in:

                                st.success(
                                    "Login successful!"
                                )

                                st.rerun()

                    render_html(
                        """
                        <div class="login-info">

                            <strong>
                                ⓘ Don't have an account?
                            </strong>

                            <br>

                            Switch to the
                            <strong>Create Account</strong>
                            tab to get started.

                        </div>
                        """
                    )


                # =================================================
                # CREATE ACCOUNT TAB
                # =================================================

                with signup_tab:

                    render_html(
                        """
                        <div class="login-card-title">
                            Create your account
                        </div>

                        <div class="login-card-description">
                            Create an account to start analyzing your data.
                        </div>
                        """
                    )

                    with st.form("signup_form"):

                        signup_username = st.text_input(
                            "Username",
                            placeholder="Choose a username",
                        )

                        signup_email = st.text_input(
                            "Email",
                            placeholder="you@example.com",
                        )

                        signup_password = st.text_input(
                            "Password",
                            type="password",
                            placeholder="Minimum 8 characters",
                        )

                        signup_submitted = st.form_submit_button(
                            "Create Account  →",
                            type="primary",
                            use_container_width=True,
                        )

                    if signup_submitted:

                        if not signup_username.strip():

                            st.warning(
                                "Please enter a username."
                            )

                        elif not signup_email.strip():

                            st.warning(
                                "Please enter your email."
                            )

                        elif len(signup_password) < 8:

                            st.warning(
                                "Password must contain at least 8 characters."
                            )

                        else:

                            with st.spinner(
                                "Creating your account..."
                            ):

                                success, message = signup_user(
                                    signup_username,
                                    signup_email,
                                    signup_password,
                                )

                            if success:

                                st.success(
                                    message
                                )

                                st.info(
                                    "You can now switch to the Login tab."
                                )

                            else:

                                st.error(
                                    message
                                )


    # ========================================================
    # RIGHT SIDE — PRODUCT VISUAL
    # ========================================================

    with right_column:

        render_html(
            """
            <div class="visual-panel">

                <!-- POWERED BADGE -->

                <div class="powered-badge">

                    <span class="powered-star">
                        ✦
                    </span>

                    POWERED BY AI

                </div>


                <!-- HEADLINE -->

                <div class="visual-title">

                    Ask
                    <span class="gradient-text">
                        Data.
                    </span>

                    <br>

                    Get
                    <span class="gradient-text">
                        Insights.
                    </span>

                    <br>

                    Make
                    <span class="gradient-text">
                        Better Decisions.
                    </span>

                </div>


                <!-- DESCRIPTION -->

                <div class="visual-description">

                    Natural language to SQL, visualizations,
                    and business insights — all in one place.

                </div>


                <!-- VISUAL GRID -->

                <div class="visual-grid">


                    <!-- LEFT VISUAL COLUMN -->

                    <div class="visual-column">


                        <!-- GENERATED SQL -->

                        <div class="visual-box">

                            <div class="visual-box-header">

                                <div class="visual-box-title">

                                    <div class="visual-icon">
                                        ▤
                                    </div>

                                    Generated SQL

                                </div>

                                <div class="visual-dots">
                                    •••
                                </div>

                            </div>


                            <div class="sql-content">

                                <div>
                                    <span class="sql-keyword">
                                        SELECT
                                    </span>
                                    region,
                                </div>

                                <div>
                                    <span class="sql-yellow">
                                        SUM
                                    </span>(sales)
                                    <span class="sql-blue">
                                        AS
                                    </span>
                                    total_sales
                                </div>

                                <div>
                                    <span class="sql-keyword">
                                        FROM
                                    </span>
                                    sales_data
                                </div>

                                <div>
                                    <span class="sql-keyword">
                                        GROUP BY
                                    </span>
                                    region
                                </div>

                                <div>
                                    <span class="sql-keyword">
                                        ORDER BY
                                    </span>
                                    total_sales
                                    <span class="sql-blue">
                                        DESC
                                    </span>
                                </div>

                                <div>
                                    <span class="sql-keyword">
                                        LIMIT
                                    </span>
                                    10;
                                </div>

                            </div>

                        </div>


                        <!-- DATABASE -->

                        <div class="visual-box">

                            <div class="database-area">

                                <div class="database-glow">
                                </div>

                                <div class="database">

                                    <div class="db-layer db-top">
                                    </div>

                                    <div class="db-layer db-middle">
                                    </div>

                                    <div class="db-layer db-bottom">
                                    </div>

                                </div>

                            </div>

                        </div>

                    </div>


                    <!-- RIGHT VISUAL COLUMN -->

                    <div class="visual-column">


                        <!-- CHART -->

                        <div class="visual-box">

                            <div class="visual-box-header">

                                <div class="visual-box-title">

                                    <div class="visual-icon">
                                        ▥
                                    </div>

                                    Sales by Region

                                </div>

                                <div class="visual-dots">
                                    •••
                                </div>

                            </div>


                            <div class="chart-content">

                                <div class="chart-area">

                                    <div class="chart-bar bar-one">
                                    </div>

                                    <div class="chart-bar bar-two">
                                    </div>

                                    <div class="chart-bar bar-three">
                                    </div>

                                    <div class="chart-bar bar-four">
                                    </div>

                                    <div class="chart-bar bar-five">
                                    </div>

                                    <div class="chart-bar bar-six">
                                    </div>

                                </div>

                            </div>

                        </div>


                        <!-- DATA PREVIEW -->

                        <div class="visual-box">

                            <div class="visual-box-header">

                                <div class="visual-box-title">

                                    <div class="visual-icon">
                                        ▤
                                    </div>

                                    Data Preview

                                </div>

                                <div class="visual-dots">
                                    •••
                                </div>

                            </div>


                            <div class="table-content">

                                <div class="table-row header">

                                    <div>#</div>
                                    <div>region</div>
                                    <div>sales</div>
                                    <div>country</div>

                                </div>


                                <div class="table-row">

                                    <div>1</div>
                                    <div>North</div>
                                    <div>76,337</div>
                                    <div>USA</div>

                                </div>


                                <div class="table-row">

                                    <div>2</div>
                                    <div>Florida</div>
                                    <div>67,500</div>
                                    <div>Canada</div>

                                </div>


                                <div class="table-row">

                                    <div>3</div>
                                    <div>Texas</div>
                                    <div>47,377</div>
                                    <div>UK</div>

                                </div>


                                <div class="table-row">

                                    <div>4</div>
                                    <div>New York</div>
                                    <div>39,877</div>
                                    <div>Germany</div>

                                </div>


                                <div class="table-row">

                                    <div>5</div>
                                    <div>California</div>
                                    <div>31,363</div>
                                    <div>France</div>

                                </div>

                            </div>

                        </div>

                    </div>

                </div>
            """
        )

    st.stop()


# ============================================================
# SIDEBAR TOGGLE BRIDGE
# ============================================================

st.html(
    """
    <style>
        #ai-data-analyst-close-toggle,
        #ai-data-analyst-open-toggle {
            position: fixed;
            z-index: 2147483647;

            display: none;

            align-items: center;
            justify-content: center;

            width: 42px;
            height: 42px;

            padding: 0;

            border-radius: 10px;

            background:
                linear-gradient(
                    135deg,
                    rgba(55, 52, 125, 0.96),
                    rgba(82, 55, 145, 0.96)
                );

            border: 1px solid
                rgba(139, 124, 255, 0.55);

            color: #ffffff;

            box-shadow:
                0 8px 22px
                rgba(0, 0, 0, 0.24);

            cursor: pointer;

            font-size: 27px;
            font-weight: 600;

            line-height: 1;
        }

        #ai-data-analyst-close-toggle:hover,
        #ai-data-analyst-open-toggle:hover {
            background:
                linear-gradient(
                    135deg,
                    #386fff,
                    #a936ff
                );

            border-color:
                rgba(180, 160, 255, 0.85);
        }

        #ai-data-analyst-open-toggle {
            top: 14px;
            left: 14px;
        }
    </style>

    <script>
    (() => {

        if (window.__aiDataAnalystSidebarToggleInstalled) {
            return;
        }

        window.__aiDataAnalystSidebarToggleInstalled = true;


        function getSidebar() {
            return document.querySelector(
                '[data-testid="stSidebar"]'
            );
        }


        function getNativeCloseButton() {
            return document.querySelector(
                '[data-testid="stSidebarCollapseButton"] button'
            );
        }


        function getNativeOpenButton() {
            return document.querySelector(
                '[data-testid="stSidebarCollapsedControl"] button'
            );
        }


        function createButtons() {

            let closeButton =
                document.getElementById(
                    'ai-data-analyst-close-toggle'
                );

            let openButton =
                document.getElementById(
                    'ai-data-analyst-open-toggle'
                );


            if (!closeButton) {

                closeButton =
                    document.createElement('button');

                closeButton.id =
                    'ai-data-analyst-close-toggle';

                closeButton.type =
                    'button';

                closeButton.textContent = '‹';

                document.body.appendChild(
                    closeButton
                );


                closeButton.addEventListener(
                    'click',
                    () => {

                        const nativeButton =
                            getNativeCloseButton();

                        if (nativeButton) {
                            nativeButton.click();
                        }

                    }
                );
            }


            if (!openButton) {

                openButton =
                    document.createElement('button');

                openButton.id =
                    'ai-data-analyst-open-toggle';

                openButton.type =
                    'button';

                openButton.textContent = '›';

                document.body.appendChild(
                    openButton
                );


                openButton.addEventListener(
                    'click',
                    () => {

                        const nativeButton =
                            getNativeOpenButton();

                        if (nativeButton) {
                            nativeButton.click();
                        }

                    }
                );
            }


            return {
                closeButton,
                openButton
            };
        }


        function updateButtons() {

            const sidebar =
                getSidebar();

            const nativeClose =
                getNativeCloseButton();

            const nativeOpen =
                getNativeOpenButton();


            if (nativeClose) {

                nativeClose.style.setProperty(
                    "visibility",
                    "hidden",
                    "important"
                );

                nativeClose.style.setProperty(
                    "opacity",
                    "0",
                    "important"
                );

                nativeClose.style.setProperty(
                    "pointer-events",
                    "none",
                    "important"
                );
            }


            if (nativeOpen) {

                nativeOpen.style.setProperty(
                    "visibility",
                    "hidden",
                    "important"
                );

                nativeOpen.style.setProperty(
                    "opacity",
                    "0",
                    "important"
                );

                nativeOpen.style.setProperty(
                    "pointer-events",
                    "none",
                    "important"
                );
            }


            const buttons =
                createButtons();

            const closeButton =
                buttons.closeButton;

            const openButton =
                buttons.openButton;


            /*
             * SIDEBAR OPEN
             */

            if (
                sidebar &&
                nativeClose
            ) {

                const rect =
                    sidebar.getBoundingClientRect();

                closeButton.style.left =
                    Math.max(
                        8,
                        rect.right - 50
                    ) + 'px';

                closeButton.style.top =
                    '16px';

                closeButton.style.display =
                    'flex';

                openButton.style.display =
                    'none';

                return;
            }


            /*
             * SIDEBAR CLOSED
             */

            if (nativeOpen) {

                closeButton.style.display =
                    'none';

                openButton.style.display =
                    'flex';

                return;
            }


            closeButton.style.display =
                'none';

            openButton.style.display =
                'none';
        }


        const observer =
            new MutationObserver(
                updateButtons
            );


        observer.observe(
            document.body,
            {
                childList: true,
                subtree: true,
                attributes: true
            }
        );


        updateButtons();


        setInterval(
            updateButtons,
            500
        );

    })();
    </script>
    """,
    unsafe_allow_javascript=True,
)

# ============================================================
# AUTHENTICATED SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # SIDEBAR BRAND
    # ========================================================

    st.html(
        """
        <div class="sidebar-brand">

            <div class="sidebar-brand-title">
            📊 AI Data Analyst
            </div>

            <div class="sidebar-brand-subtitle">
            Natural language data analysis
            </div>

        </div>
        """
    )

    st.divider()


    # ========================================================
    # DATA SOURCE
    # ========================================================

    st.markdown(
        "### 📁 Data Source"
    )

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx", "xls"],
        help="Upload the dataset you want to analyze.",
        label_visibility="collapsed",
    )


    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(".csv"):

                uploaded_df = pd.read_csv(
                    uploaded_file
                )

            else:

                uploaded_df = pd.read_excel(
                    uploaded_file
                )

            st.session_state.uploaded_dataset = uploaded_df
            st.session_state.uploaded_dataset_name = (
                uploaded_file.name
            )

            st.success(
                f"✓ {uploaded_file.name}",
                icon="📁",
            )

        except Exception as exc:

            st.error(
                f"Could not read file: {exc}"
            )

    elif st.session_state.uploaded_dataset is None:

        st.caption(
            "No dataset loaded"
        )


    # ========================================================
    # DATASET
    # ========================================================

    st.divider()

    st.markdown(
        "### 🗂 Dataset"
    )

    if st.session_state.uploaded_dataset is not None:

        dataset = st.session_state.uploaded_dataset

        row_count = dataset.shape[0]
        column_count = dataset.shape[1]

        render_html(
            f"""
            <div class="dataset-info-card">

                <div class="dataset-file-name">
                    📄 {st.session_state.uploaded_dataset_name}
                </div>

                <div class="dataset-stats">

                    <span>
                        <strong>{row_count:,}</strong><br>
                        Rows
                    </span>

                    <span>
                        <strong>{column_count}</strong><br>
                        Columns
                    </span>
                </div>

            </div>
        """
        )

        if st.button(
            "👁 Preview Data",
            key="preview_dataset_button",
            use_container_width=True,
        ):

            st.session_state.preview_dataset = (
                not st.session_state.preview_dataset
            )

    else:

        st.markdown(
            """
            <div class="sidebar-compact-description">
                Upload a dataset to see its details.
            </div>
            """,
            unsafe_allow_html=True,
        )


    # ========================================================
    # ANALYSIS HISTORY
    # ========================================================

    st.divider()

    st.markdown(
        "### 🕘 Analysis History"
    )

    try:
        history_response = requests.get(
            f"{API_BASE_URL}/api/analysis/history",
            headers={
                "Authorization": (
                    f"Bearer {st.session_state.access_token}"
                )
            },
            timeout=30,
        )

        if history_response.status_code == 200:
            history_data = history_response.json()
            st.session_state.analysis_history = (
                history_data.get("history", [])
            )

    except Exception:
        pass

    if st.session_state.analysis_history:

        for history_item in st.session_state.analysis_history:

            history_question = history_item["question"]
            history_id = history_item["id"]

            history_col, delete_col = st.columns(
                [5, 1],
                gap="small",
            )

            with history_col:

                if st.button(
                    history_question,
                    key=f"history_{history_id}",
                    use_container_width=True,
                ):
                    st.session_state.selected_question = (
                        history_question
                    )
                    st.rerun()

            with delete_col:

                if st.button(
                    "🗑️",
                    key=f"delete_history_{history_id}",
                    help="Delete this analysis",
                ):
                    delete_response = requests.delete(
                        f"{API_BASE_URL}/api/analysis/history/"
                        f"{history_id}",
                        headers={
                            "Authorization": (
                                f"Bearer "
                                f"{st.session_state.access_token}"
                            )
                        },
                        timeout=30,
                    )

                    if delete_response.status_code == 200:
                        st.session_state.analysis_history = [
                            item
                            for item in st.session_state.analysis_history
                            if item["id"] != history_id
                        ]

                        st.rerun()

    else:

        st.markdown(
            """
            <div class="sidebar-compact-description">
                Your recent analyses will appear here.
            </div>
            """,
            unsafe_allow_html=True,
        )


    # ========================================================
    # TRY ASKING
    # ========================================================

    st.divider()

    st.markdown(
        "### 💡 Try Asking"
    )

    example_questions = [
        "Which state has the most customers?",
        "Show the top 10 states by customer count.",
        "What is the average order amount?",
        "Which product category has the most products?",
    ]

    for index, example in enumerate(
        example_questions
    ):

        if st.button(
            example,
            key=f"example_{index}",
            use_container_width=True,
        ):

            st.session_state.selected_question = (
                example
            )

            st.rerun()


    # ========================================================
    # ACCOUNT
    # ========================================================

    st.divider()

    st.markdown(
        f"### 👤 Account : **{st.session_state.username}**"
    )

    if st.button(
        "Logout",
        key="logout_button",
        use_container_width=True,
    ):

        st.session_state.access_token = None
        st.session_state.username = None
        cookies["access_token"] = ""
        cookies["username"] = ""
        cookies.save()
        st.session_state.analysis_result = None
        st.session_state.uploaded_dataset = None
        st.session_state.uploaded_dataset_name = None
        st.session_state.analysis_history = []
        st.session_state.preview_dataset = False
        st.session_state.selected_question = ""

        st.rerun()


# WORKSPACE HEADER
# ============================================================

render_html(
    """
    <div class="workspace-header">

        <div class="workspace-title">
            Ask questions about your data in plain English
            and get SQL, insights, and visualizations.
        </div>

    </div>
    """
)


# ============================================================
# DATA PREVIEW
# ============================================================

if (
    st.session_state.preview_dataset
    and st.session_state.uploaded_dataset is not None
):

    st.divider()

    st.subheader("Data Preview")

    st.dataframe(
        st.session_state.uploaded_dataset,
        use_container_width=True,
        hide_index=True,
    )

# ============================================================
# QUESTION INPUT
# ============================================================


question = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: Which state has the most customers?"
    ),
    height=100,
)

analyze_button = st.button(
    "🔎 Analyze Data",
    type="primary",
    use_container_width=True,
)


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button:

    if not question.strip():

        st.warning(
            "Please enter a question first."
        )

    else:

        with st.spinner(
            "Analyzing your data..."
        ):

            result = run_analysis(
                question.strip()
            )

        if result is not None:
            st.session_state.analysis_result = result

            st.session_state.analysis_history.append(
                {
                    "question": question.strip(),
                }
            )

            


# ============================================================
# DISPLAY ANALYSIS RESULT
# ============================================================

result = st.session_state.analysis_result


if result:

    st.divider()


    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Rows",
            result.get(
                "row_count",
                0,
            ),
        )

    with col2:

        st.metric(
            "Columns",
            result.get(
                "column_count",
                0,
            ),
        )

    with col3:

        chart_status = (
            "Available"
            if result.get(
                "chart_available",
                False,
            )
            else "Not available"
        )

        st.metric(
            "Visualization",
            chart_status,
        )


    # ========================================================
    # AI INSIGHT
    # ========================================================

    st.markdown(
        "### 🧠 AI Insight"
    )

    insight = result.get(
        "insight",
        "No insight available.",
    )

    safe_insight = html.escape(
        str(insight)
    ).replace(
        "\n",
        "<br>",
    )

    render_html(
        f"""
        <div class="insight-box">
            {safe_insight}
        </div>
        """
    )


    # ========================================================
    # VISUALIZATION
    # ========================================================

    chart_json = result.get(
        "chart"
    )

    if chart_json:

        st.markdown(
            "### 📈 Visualization"
        )

        try:

            figure = go.Figure(
                chart_json
            )

            st.plotly_chart(
                figure,
                use_container_width=True,
            )

        except Exception as exc:

            st.warning(
                f"Could not render the chart: {exc}"
            )


    # ========================================================
    # QUERY RESULT
    # ========================================================

    st.markdown(
        "### 📋 Query Result"
    )

    result_data = result.get(
        "data",
        [],
    )

    if result_data:

        result_dataframe = pd.DataFrame(
            result_data
        )

        st.dataframe(
            result_dataframe,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "The query returned no rows."
        )


    # ========================================================
    # GENERATED SQL
    # ========================================================

    st.markdown(
        "### 🧾 Generated SQL"
    )

    st.code(
        result.get(
            "sql",
            "",
        ),
        language="sql",
    )


    # ========================================================
    # DETAILED ANALYSIS
    # ========================================================

    with st.expander(
        "View detailed data analysis"
    ):

        analysis = result.get(
            "analysis",
            {},
        )

        st.json(
            analysis
        )