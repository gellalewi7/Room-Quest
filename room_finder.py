import base64
from datetime import datetime, timedelta
from io import BytesIO
import json
import os
import re
import urllib.parse
import pandas as pd
from PIL import Image
import streamlit as st

try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
    def get_device_id():
        ctx = get_script_run_ctx()
        return ctx.session_id if ctx else "default_device_id"
except Exception:
    def get_device_id():
        return "default_device_id"

st.set_page_config(page_title="🏠Room Quest", page_icon="🏠", layout="wide", initial_sidebar_state="expanded")

# ===== FC26 THEME - ELECTRIC BLUE + NEON GREEN + TRANSPARENT GLASS BLEND =====
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }

/* MAIN - YOUR ORIGINAL BLUE UI ON RIGHT */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at bottom right, #3B82F6 0%, #1E3A8A 25%, #1E293B 60%, #0F172A 85%) !important;
    background-attachment: fixed !important;
}
[data-testid="stHeader"] { background: transparent !important; }
h1 { color: #FFFFFF !important; font-weight: 900 !important; }

/* LEFT SIDEBAR - FC26 NEON */
section[data-testid="stSidebar"] {
    background: 
        radial-gradient(ellipse at 10% 15%, rgba(0,255,136,0.38) 0%, transparent 52%),
        radial-gradient(ellipse at 85% 25%, rgba(0,217,255,0.48) 0%, transparent 55%),
        linear-gradient(180deg, #020617 0%, #081A36 18%, #0E2A5E 42%, #104B8A 72%, #0C6CB6 92%) !important;
}
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    background: rgba(255,255,255,0.09) !important; border: 1px solid rgba(0,217,255,0.28) !important;
    padding: 12px 14px !important; border-radius: 12px !important; margin-bottom: 8px !important; font-weight: 700 !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] {
    background: linear-gradient(135deg, rgba(0,217,255,0.92) 0%, rgba(0,255,136,0.85) 100%) !important;
}
section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"] * { color: #020617 !important; }

/* EXPANDER / FORM - WHITE GLASS - NO BLUE */
[data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stExpander"], div[data-testid="stForm"] {
    background: rgba(255,255,255,0.16) !important;
    backdrop-filter: blur(22px) !important;
    -webkit-backdrop-filter: blur(22px) !important;
    border-radius: 18px !important; 
    border: 1px solid rgba(255,255,255,0.28) !important;
    box-shadow: 0 10px 36px rgba(0,0,0,0.20), 0 0 0 1px rgba(0,217,255,0.18), inset 0 1px 0 rgba(255,255,255,0.25) !important;
}
div[data-testid="stExpander"] summary {
    background: #FFFFFF !important; color: #0F172A !important;
    font-weight: 800 !important; font-size: 14px !important; padding: 14px 16px !important; border-radius: 10px !important;
    border: 1px solid #CBD5E1 !important;
}
div[data-testid="stExpander"] summary span, div[data-testid="stExpander"] summary p { color: #0F172A !important; font-weight: 800 !important; }
div[data-testid="stExpander"] summary svg { fill: #0F172A !important; }


/* LOGIN RADIO - TENANT/LANDLORD VISIBLE - FIX WHITE COVER */
section[data-testid="stSidebar"] div[role="radiogroup"] label,
div[data-testid="stRadio"] label {
    background: rgba(255,255,255,0.92) !important;
    border: 1.5px solid #CBD5E1 !important;
    color: #0F172A !important;
    opacity: 1 !important;
}
div[data-testid="stRadio"] label p, div[data-testid="stRadio"] label span,
section[data-testid="stSidebar"] div[role="radiogroup"] label p,
section[data-testid="stSidebar"] div[role="radiogroup"] label span {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
    background: #0F172A !important;
    border-color: #0F172A !important;
}
div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] * {
    color: #FFFFFF !important;
}

/* LOGIN CONTAINER - TRANSPARENT BLEND */

/* ===== ALL LABELS ABOVE CARDS/BUTTONS IN EVERY TAB - 100% VISIBLE ===== */
div[data-testid="stTextInput"] > label,
div[data-testid="stTextArea"] > label,
div[data-testid="stNumberInput"] > label,
div[data-testid="stSelectbox"] > label,
div[data-testid="stFileUploader"] > label,
div[data-testid="stCheckbox"] > label,
div[data-testid="stRadio"] > label,
label[data-testid="stWidgetLabel"],
div[data-baseweb="select"] + label,
[data-testid="stExpander"] label,
[data-testid="stForm"] label {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    background: #FFFFFF !important;
    background-color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 12.5px !important;
    letter-spacing: 0.3px !important;
    padding: 5px 12px !important;
    border-radius: 8px !important;
    border: 1.5px solid #CBD5E1 !important;
    opacity: 1 !important;
    display: inline-block !important;
    margin-bottom: 6px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    text-transform: uppercase !important;
}
div[data-testid="stTextInput"] > label p,
div[data-testid="stTextArea"] > label p,
div[data-testid="stSelectbox"] > label p,
div[data-testid="stFileUploader"] > label p,
label[data-testid="stWidgetLabel"] p {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    font-weight: 800 !important;
    opacity: 1 !important;
}
/* Fix Primary Operating Area and similar faint labels */
div[data-testid="stExpander"] p, div[data-testid="stForm"] p,
div[data-testid="stExpander"] span, div[data-testid="stForm"] span {
    color: #0F172A !important;
    opacity: 1 !important;
}

/* INPUTS - WHITE */
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
    background: #FFFFFF !important; border: 1.5px solid #CBD5E1 !important;
    color: #0F172A !important; font-weight: 600 !important; border-radius: 10px !important;
    -webkit-text-fill-color: #0F172A !important;
}

/* TABS - VISIBLE + TRANSPARENT */
div[data-testid="stTabs"] [data-baseweb="tab-list"] { 
    background: rgba(255,255,255,0.92) !important; border-radius: 12px !important; 
    border: 1px solid #E2E8F0 !important; padding: 5px !important; gap: 5px !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent !important; color: #475569 !important; border-radius: 8px !important; font-weight: 700 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
    background: #0F172A !important; color: #FFFFFF !important;
}

/* ===== DROPDOWNS - PURE WHITE - ZERO BLUE PATCH - LIKE HOME ALL LOCATIONS ===== */
div[data-testid="stSelectbox"] { background: transparent !important; }
div[data-testid="stSelectbox"] > label {
    color: #0F172A !important; font-weight: 800 !important; font-size: 11px !important;
    background: #FFFFFF !important; padding: 4px 10px !important; border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important; margin-bottom: 6px !important; display: inline-block !important;
}
div[data-baseweb="select"] { background: transparent !important; }
div[data-baseweb="select"] > div {
    background: #FFFFFF !important; background-color: #FFFFFF !important; background-image: none !important;
    border: 1.5px solid #CBD5E1 !important; border-radius: 10px !important; min-height: 46px !important;
    box-shadow: none !important;
}
div[data-baseweb="select"] > div > div { background: #FFFFFF !important; background-color: #FFFFFF !important; background-image: none !important; }
div[data-baseweb="select"] span, div[data-baseweb="select"] div {
    color: #0F172A !important; -webkit-text-fill-color: #0F172A !important; font-weight: 600 !important;
    background: transparent !important;
}
div[data-baseweb="select"] svg { fill: #64748B !important; }
div[data-baseweb="popover"] > div {
    background: #FFFFFF !important; border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important; box-shadow: 0 10px 25px rgba(0,0,0,0.15) !important;
}
ul[data-baseweb="menu"] { background: #FFFFFF !important; }
li[role="option"] { background: #FFFFFF !important; color: #0F172A !important; padding: 10px 12px !important; }
li[role="option"]:hover { background: #F1F5F9 !important; }
li[role="option"][aria-selected="true"] { background: #0F172A !important; color: #FFFFFF !important; }

/* FINAL OVERRIDE - KILL ANY REMAINING BLUE INSIDE EXPANDER/FORM */
div[data-testid="stExpander"] div[data-baseweb="select"] *,
div[data-testid="stForm"] div[data-baseweb="select"] * {
    background-color: #FFFFFF !important; background-image: none !important;
}
div[data-testid="stExpander"] div[data-baseweb="select"] > div,
div[data-testid="stForm"] div[data-baseweb="select"] > div {
    background: #FFFFFF !important; background-color: #FFFFFF !important; background-image: none !important;
    border: 1.5px solid #CBD5E1 !important;
}

/* NO PHOTO CARD - PURE WHITE WITH TEXT - VISIBLE */
.placeholder-house {
    height: 260px !important; width: 100% !important;
    background: #FFFFFF !important; background-color: #FFFFFF !important;
    border: 2px dashed #94A3B8 !important;
    border-radius: 12px !important; 
    display: flex !important; align-items: center !important; justify-content: center !important; flex-direction: column !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
}
.placeholder-house .ph-icon { font-size: 56px !important; opacity: 0.9; margin-bottom: 10px; }
.placeholder-house .ph-text {
    color: #0F172A !important; font-weight: 800 !important; font-size: 13px !important;
    background: #F1F5F9 !important; padding: 6px 14px !important; border-radius: 20px !important;
    border: 1px solid #CBD5E1 !important; letter-spacing: 0.5px; text-transform: uppercase;
}

/* RULES CARD - VISIBLE PRESENTABLE */
.rules-card {
    background: #FFFBEB !important; border: 1px solid #FDE68A !important; border-left: 5px solid #F59E0B !important;
    border-radius: 10px !important; padding: 12px 14px !important; margin: 8px 0 !important;
}
.rules-card .rules-header { font-weight: 800 !important; color: #92400E !important; font-size: 11px !important; text-transform: uppercase; margin-bottom: 4px; }
.rules-card .rules-text { color: #78350F !important; font-weight: 600 !important; font-size: 13px !important; }



/* ALL WHITE CARDS LIT TRANSPARENCY FC26 BLEND */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.18) !important;
    backdrop-filter: blur(20px) !important;
}
div[data-testid="stExpander"] {
    background: rgba(255,255,255,0.20) !important;
    backdrop-filter: blur(20px) !important;
}

/* DASHBOARD NOTIFICATION - RECTANGULAR WITH FAINT WHITE LINE */
.dashboard-notif {
    background: rgba(255,255,255,0.16) !important;
    backdrop-filter: blur(18px) !important;
    border: 2.5px solid #FFFFFF !important;
    border-radius: 14px !important;
    padding: 16px !important;
    margin: 10px 0 !important;
    box-shadow: 0 6px 20px rgba(0,0,0,0.15) !important;
}
/* NEW: Verification rectangular cards */
.verified-notif-card {
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin: 10px 0 !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12) !important;
    display: block !important;
    width: 100% !important;
}
.verified-notif-card * {
    color: #FFFFFF !important;
}
.verified-notif-card code {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.25) !important;
    padding: 2px 8px !important;
    border-radius: 4px !important;
    color: #FEF08A !important;
    font-weight: 700 !important;
}
.status-box-approved-new {
    background: rgba(255,255,255,0.10) !important;
    border: 1px solid rgba(255,255,255,0.40) !important;
    border-left: 4px solid #00FF88 !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin: 10px 0 !important;
}
.status-box-pending-new {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    border-left: 4px solid #FACC15 !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin: 10px 0 !important;
}
.status-box-error-new {
    background: rgba(239,68,68,0.12) !important;
    border: 1px solid rgba(255,255,255,0.30) !important;
    border-left: 4px solid #EF4444 !important;
    border-radius: 8px !important;
    padding: 14px 16px !important;
    margin: 10px 0 !important;
}


/* ===== FIX: UPLOAD BUTTONS VISIBLE ENTIRE SYSTEM ===== */
div[data-testid="stFileUploader"] button {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: 2px solid #0F172A !important;
    font-weight: 800 !important;
    font-size: 14px !important;
    opacity: 1 !important;
    visibility: visible !important;
    display: inline-flex !important;
}
div[data-testid="stFileUploader"] button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    opacity: 1 !important;
}
div[data-testid="stFileUploader"] section {
    background: #FFFFFF !important;
    border: 2px dashed #0F172A !important;
    border-radius: 12px !important;
    opacity: 1 !important;
}
div[data-testid="stFileUploader"] section * {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
}
div[data-testid="stFileUploader"] label {
    background: #FFFFFF !important;
    color: #0F172A !important;
    border: 1.5px solid #CBD5E1 !important;
    font-weight: 800 !important;
}

/* BUTTONS & BANNERS - 100% VISIBLE */
.stButton > button, div[data-testid="stForm"] button, button[kind="primary"], button[kind="primaryFormSubmit"] {
    background: #0F172A !important; color: #FFFFFF !important; 
    border-radius: 10px !important; font-weight: 800 !important;
    opacity: 1 !important; visibility: visible !important;
    border: 2px solid #0F172A !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}
.stButton > button *, div[data-testid="stForm"] button * { color: #FFFFFF !important; opacity: 1 !important; }

/* FILE UPLOADER - VISIBLE */
div[data-testid="stFileUploader"] { background: #FFFFFF !important; border-radius: 10px !important; padding: 8px !important; }
div[data-testid="stFileUploader"] section {
    background: #FFFFFF !important; border: 2px dashed #94A3B8 !important;
    border-radius: 10px !important; padding: 14px !important;
}
div[data-testid="stFileUploader"] section * { color: #0F172A !important; opacity: 1 !important; font-weight: 600 !important; }
div[data-testid="stFileUploader"] button {
    background: #0F172A !important; color: #FFFFFF !important; 
    border-radius: 8px !important; opacity: 1 !important; visibility: visible !important;
    border: 1.5px solid #0F172A !important; font-weight: 800 !important;
}
div[data-testid="stFileUploader"] small { color: #475569 !important; opacity: 1 !important; }

/* ECOCASH BANNER - ALL TEXT VISIBLE */
.ecocash-banner { 
    background: #FFFFFF !important; border: 2.5px solid #16A34A !important; 
    border-radius: 14px !important; padding: 18px !important; text-align: center !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08) !important;
}
.ecocash-banner * { color: #0F172A !important; opacity: 1 !important; visibility: visible !important; }
.ecocash-banner h3 { color: #14532D !important; font-weight: 900 !important; font-size: 18px !important; opacity: 1 !important; }
.ecocash-banner .eco-name { color: #0F172A !important; font-weight: 800 !important; font-size: 16px !important; opacity: 1 !important; }
.ecocash-banner .eco-number { color: #16A34A !important; font-weight: 900 !important; font-size: 26px !important; opacity: 1 !important; }
.ecocash-banner p { color: #334155 !important; font-weight: 600 !important; opacity: 1 !important; }

/* ALL ALERTS / INFO BANNERS VISIBLE */
[data-testid="stAlert"], [data-testid="stNotification"], .stAlert {
    background: #FFFFFF !important; border: 1.5px solid #CBD5E1 !important;
    border-radius: 10px !important; opacity: 1 !important; visibility: visible !important;
}
[data-testid="stAlert"] *, [data-testid="stNotification"] *, .stAlert * {
    color: #0F172A !important; opacity: 1 !important; visibility: visible !important;
}
[data-testid="stAlert"] p, [data-testid="stAlert"] span { color: #0F172A !important; opacity: 1 !important; }

/* PAYMENT PACKAGE LABELS - VISIBLE */
div[data-testid="stExpander"] h5, div[data-testid="stForm"] h5, 
div[data-testid="stExpander"] h4, div[data-testid="stForm"] h4 {
    color: #0F172A !important; background: #FFFFFF !important; 
    padding: 6px 12px !important; border-radius: 8px !important;
    border: 1px solid #E2E8F0 !important; font-weight: 800 !important;
    opacity: 1 !important; display: inline-block !important;
}

.featured-badge { background: #FEF3C7 !important; color: #78350F !important; padding: 4px 10px; border-radius: 14px; font-weight: 800; font-size: 11px; }
.hot-deal-badge { background: #0F172A !important; color: #FFFFFF !important; padding: 5px 12px; border-radius: 16px; font-weight: 800; font-size: 12px; }
.countdown-badge { background: #0F172A !important; color: #38BDF8 !important; padding: 4px 8px; border-radius: 8px; font-weight: 700; font-size: 10px; }
.wa-float-wrapper { position: fixed !important; bottom: 20px !important; right: 20px !important; z-index: 999999 !important; transform: translateZ(0) !important; -webkit-transform: translateZ(0) !important; will-change: transform !important; pointer-events: auto !important; }
.wa-float-wrapper ~ .wa-float-wrapper { display: none !important; }
.wa-float-main { animation: none !important; transition: none !important; }

.wa-float-main { background: #FFFFFF !important; border-radius: 40px; padding: 6px 6px 6px 12px; display: flex; align-items: center; gap: 10px; box-shadow: 0 8px 20px rgba(0,0,0,0.2); text-decoration: none !important; border: 1px solid #E2E8F0; }
.wa-float-icon { width: 44px; height: 44px; background: #25D366; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 24px; }
.wa-float-join { background: #0F172A; color: #FFFFFF !important; padding: 8px 14px; border-radius: 20px; font-weight: 800; font-size: 12px; }

/* ===== NEW PREMIUM AD BANNERS - BLENDS WITH UI ===== */
.feature-ad-banner {
    background: linear-gradient(135deg, rgba(255,255,255,0.22) 0%, rgba(254,249,195,0.28) 100%) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 2.5px solid #FFFFFF !important;
    border-left: 6px solid #FACC15 !important;
    border-radius: 18px !important;
    padding: 18px 20px !important;
    margin: 14px 0 18px 0 !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.18), 0 0 0 1px rgba(250,204,21,0.25), inset 0 1px 0 rgba(255,255,255,0.35) !important;
}
.feature-ad-banner .ad-title {
    color: #0F172A !important;
    background: #FEF9C3 !important;
    padding: 8px 16px !important;
    border-radius: 10px !important;
    border: 2px solid #FACC15 !important;
    font-weight: 900 !important;
    font-size: 14px !important;
    display: inline-block !important;
    margin-bottom: 10px !important;
    box-shadow: 0 2px 8px rgba(250,204,21,0.3) !important;
    -webkit-text-fill-color: #422006 !important;
}
.feature-ad-banner .ad-main {
    color: #FFFFFF !important;
    font-weight: 800 !important;
    font-size: 15px !important;
    line-height: 1.4 !important;
    margin: 6px 0 !important;
}
.feature-ad-banner .ad-prices {
    display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px;
}
.feature-ad-banner .price-pill {
    background: #0F172A !important;
    color: #FEF08A !important;
    padding: 6px 14px !important;
    border-radius: 20px !important;
    font-weight: 800 !important;
    font-size: 12px !important;
    border: 1.5px solid rgba(250,204,21,0.5) !important;
}
.feature-ad-banner .price-pill.green { background: #14532D !important; color: #BBF7D0 !important; border-color: #16A34A !important; }
.feature-ad-banner .price-pill.blue { background: #1E3A8A !important; color: #BFDBFE !important; border-color: #3B82F6 !important; }
.feature-ad-banner .ad-footer {
    color: #DBEAFE !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    margin-top: 8px !important;
}

/* Dashboard landlord tip enhanced */
.landlord-super-banner {
    background: radial-gradient(ellipse at top left, rgba(0,255,136,0.22) 0%, transparent 55%), 
                linear-gradient(135deg, rgba(15,23,42,0.94) 0%, rgba(30,58,138,0.92) 100%) !important;
    backdrop-filter: blur(20px) !important;
    border: 3px solid #FACC15 !important;
    border-radius: 20px !important;
    padding: 22px !important;
    margin: 16px 0 !important;
    box-shadow: 0 12px 32px rgba(0,0,0,0.32), 0 0 0 2px rgba(250,204,21,0.25) !important;
}

/* Footer fixed - no black/grey, matches logo */
.gella-footer-fixed {
    text-align: center;
    padding: 22px 16px;
    background: linear-gradient(135deg, rgba(255,255,255,0.20) 0%, rgba(254,249,195,0.22) 100%) !important;
    backdrop-filter: blur(18px) !important;
    border-radius: 18px;
    border: 2.5px solid #FFFFFF !important;
    border-top: 4px solid #FACC15 !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.35) !important;
    margin-top: 24px;
}
.gella-footer-fixed .logo-pill {
    color: #422006 !important;
    font-size: 16px;
    font-weight: 900;
    background: #FEF9C3 !important;
    padding: 10px 24px;
    border-radius: 14px;
    border: 2.5px solid #FACC15;
    display: inline-block;
    margin: 0;
    letter-spacing: 0.4px;
    box-shadow: 0 3px 12px rgba(250,204,21,0.4);
    -webkit-text-fill-color: #422006 !important;
}

/* ===== FINAL FIX: ALL UPLOAD BUTTONS TEXT WHITE - HIGH VISIBILITY ===== */
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] button *,
div[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background: #0F172A !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    visibility: visible !important;
}
div[data-testid="stFileUploader"] button p,
div[data-testid="stFileUploader"] button span,
div[data-testid="stFileUploader"] button div {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* Browse files button specific */
div[data-testid="stFileUploader"] section button {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: 1.5px solid #FFFFFF !important;
}
div[data-testid="stFileUploader"] section button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* The file cards themselves */
div[data-testid="stFileUploader"] section div[data-testid="stFileUploaderFile"] {
    background: #FFFFFF !important;
}
div[data-testid="stFileUploader"] section div[data-testid="stFileUploaderFile"] * {
    color: #0F172A !important;
}
/* WHY TRUST US CARDS - BLUE TRANSPARENT LIKE GELLA */
.gella-footer-fixed div[style*="background:rgba(255,255,255,0.14)"] {
    background: rgba(15,23,42,0.55) !important;
    border: 1.5px solid rgba(0,217,255,0.45) !important;
    backdrop-filter: blur(12px) !important;
}
/* Remove grey/blue/black solid backgrounds */
div[style*="background:rgba(255,255,255,0.14)"][style*="border-radius:12px"] {
    background: rgba(59,130,246,0.75) !important;
    border: 1.5px solid rgba(0,217,255,0.40) !important;
}
/* Login note white */
div[data-testid="stAppViewContainer"] p[style*="One phone number"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

</style>

<div class="wa-float-wrapper" id="waFloatWrapper">
    <a href="https://chat.whatsapp.com/GGqmwGOyOktEQEX71fBiFl?s=cl&p=a&mlu=4&ilr=4" target="_blank" class="wa-float-main" style="text-decoration:none;">
        <div class="wa-float-icon">💬</div>
        <div><strong style="display:block; color:#0F172A !important; font-size:14px; font-weight:800;">Join Mutare Group</strong><span style="display:block; color:#475569 !important; font-size:12px;">Instant room updates</span></div>
        <div class="wa-float-join">Join Now →</div>
    </a>
</div>
""", unsafe_allow_html=True)


# ===== RESET ALL DATA - CLEAN APP MODE =====
def reset_all_app_data():
    clean = {"rooms": [], "student_rooms": [], "requests": [], "student_requests": [], "houses_sale": [], "car_hire": [], "users": [], "banned_phones": [], "logged_out_phones": [], "pending_payments": [], "approved_payments": [], "verified_references": [], "activity_logs": [], "device_slots": {}, "hot_deals": [None, None, None]}
    try:
        with open(DB_FILE, "w") as f:
            json.dump(clean, f, indent=4)
        # Also clean session files if exist
        for fp in [SESSION_FILE, SEEN_FILE]:
            if os.path.exists(fp):
                try:
                    os.remove(fp)
                except:
                    pass
    except Exception as e:
        pass
    return clean

# Auto-clean if database has old data - uncomment next line to force clean on every restart
# To make app new: we will clean if DB contains any rooms/payments on first import

DB_FILE = "mutarerooms_db.json"
SESSION_FILE = "mutare_session.json"
SEEN_FILE = "mutare_seen.json"
ADMIN_PASSWORD = "wheezyouttahere"
ADMIN_NAME = "lewis g kajayi"
ADMIN_PHONES = ["0789851813","0712181037","263789851813","263712181037","789851813","712181037"]

def canonical_phone(p):
    """Normalize Zimbabwe numbers: 2637... -> 07... , keep canonical 07 form for matching"""
    d = re.sub(r"\D", "", str(p))
    if not d:
        return d
    if d.startswith("263") and len(d) >= 11:
        d = "0" + d[3:]
    if len(d) == 9:
        d = "0" + d
    return d



def format_countdown(expires_at_str):
    if not expires_at_str: return None
    try:
        exp_dt = datetime.fromisoformat(expires_at_str)
        now = datetime.now()
        diff = exp_dt - now
        if diff.total_seconds() <= 0: return "Expired - Depleted"
        days = diff.days; hours = diff.seconds // 3600; minutes = (diff.seconds % 3600) // 60
        if days > 0: return f"⏰ Expires in: {days}d {hours}h {minutes}m"
        return f"⏰ Expires in: {hours}h {minutes}m"
    except Exception: return None

def process_uploaded_image(uploaded_file):
    if uploaded_file is None: return None
    try:
        file_bytes = uploaded_file.getvalue()
        if not file_bytes: return None
        img = Image.open(BytesIO(file_bytes))
        if img.mode!= "RGB": img = img.convert("RGB")
        buffer = BytesIO(); img.save(buffer, format="JPEG", quality=85)
        encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        st.error(f"Error processing image file: {e}"); return None

def is_image_duplicate(data, new_img_encoded):
    if not new_img_encoded: return False
    for category in ["rooms", "student_rooms", "houses_sale"]:
        for item in data.get(category, []):
            for existing_img in item.get("imgs", []):
                if existing_img and isinstance(existing_img, str) and existing_img == new_img_encoded: return True
    return False

def save_persistent_db(data):
    try:
        with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving database: {e}"); return False


def cleanup_expired_items(data):
    now = datetime.now()
    modified = False
    # --- ROOMS / STUDENT / HOUSES ---
    for category in ["rooms", "student_rooms", "houses_sale"]:
        valid_items = []
        for item in data.get(category, []):
            expires_at_str = item.get("expires_at")
            is_featured = item.get("is_featured", False)
            featured_until_str = item.get("featured_until")
            featured_days = item.get("featured_days", 0)
            # Check featured expiry first
            if is_featured and featured_until_str:
                try:
                    until_dt = datetime.fromisoformat(featured_until_str)
                    if now > until_dt:
                        # FEATURED EXPIRED
                        if featured_days == 7 or featured_days == 0:  # default 7d treat as shuffle back
                            # Remove from featured, shuffle to normal with 21 days new countdown
                            item["is_featured"] = False
                            item["featured_until"] = None
                            item["featured_days"] = None
                            item["expires_at"] = (now + timedelta(days=21)).isoformat()
                            item["was_featured_expired_to_normal"] = True
                            modified = True
                            # keep item (shuffle to all rooms)
                            valid_items.append(item)
                            continue
                        elif featured_days >= 30:
                            # 30 days featured - remove completely, do not shuffle
                            modified = True
                            continue
                        else:
                            # other durations - treat as 7d shuffle
                            item["is_featured"] = False
                            item["featured_until"] = None
                            item["featured_days"] = None
                            item["expires_at"] = (now + timedelta(days=21)).isoformat()
                            modified = True
                            valid_items.append(item)
                            continue
                except Exception:
                    pass
            # Check normal expiry
            if expires_at_str:
                try:
                    exp_dt = datetime.fromisoformat(expires_at_str)
                    if now <= exp_dt:
                        valid_items.append(item)
                    else:
                        modified = True
                        # expired normal listing - remove
                except Exception:
                    valid_items.append(item)
            else:
                # No expiry - set 21 days
                created_str = item.get("created_at", now.isoformat())
                try:
                    created_dt = datetime.fromisoformat(created_str)
                    if now - created_dt <= timedelta(days=21):
                        item["expires_at"] = (created_dt + timedelta(days=21)).isoformat()
                        valid_items.append(item)
                    else:
                        modified = True
                except Exception:
                    valid_items.append(item)
        data[category] = valid_items

    # --- REQUESTS 21 days auto-delete ---
    for req_key in ["requests", "student_requests"]:
        valid_requests = []
        for req in data.get(req_key, []):
            created_at_str = req.get("created_at")
            if created_at_str:
                try:
                    created_at = datetime.fromisoformat(created_at_str)
                    if now - created_at <= timedelta(days=21):
                        valid_requests.append(req)
                    else:
                        modified = True
                except Exception:
                    valid_requests.append(req)
            else:
                req["created_at"] = now.isoformat()
                valid_requests.append(req)
                modified = True
        data[req_key] = valid_requests

    # --- HOT DEALS 7 days -> back to normal 21 days ---
    hot_deals = data.get("hot_deals", [None, None, None])
    for i in range(len(hot_deals)):
        deal = hot_deals[i]
        if deal and isinstance(deal, dict):
            expires_at = deal.get("expires_at")
            origin_id = deal.get("id")
            origin_db_key = deal.get("_origin_db_key", "rooms")
            if expires_at:
                try:
                    if now > datetime.fromisoformat(expires_at):
                        # Expired hot slot - remove from slot
                        hot_deals[i] = None
                        modified = True
                        # Find original listing and reshuffle to normal with 21 days
                        for item in data.get(origin_db_key, []):
                            if item.get("id") == origin_id:
                                item["is_featured"] = False
                                item["featured_until"] = None
                                item["featured_days"] = None
                                item["is_hot_deal"] = False
                                item["expires_at"] = (now + timedelta(days=21)).isoformat()
                                break
                except Exception:
                    pass
    data["hot_deals"] = hot_deals

    # --- USERS: VIP, AGENT PACKAGES, FREE SLOT RESET ---
    for u in data.get("users", []):
        # VIP House Sale 30d unlimited
        if u.get("is_vip"):
            until_str = u.get("vip_until")
            if until_str:
                try:
                    if now > datetime.fromisoformat(until_str):
                        u["is_vip"] = False
                        u["vip_until"] = None
                        modified = True
                except Exception:
                    pass
        # AGENT PACKAGES
        if u.get("agent_package"):
            until_str = u.get("agent_package_until")
            if until_str:
                try:
                    if now > datetime.fromisoformat(until_str):
                        # Package expired - deplete listings beyond 5 free
                        phone = u.get("phone")
                        # Keep only 5 most recent rooms, delete rest posted during agent period
                        rooms = [r for r in data.get("rooms", []) if r.get("posted_by_phone") == phone]
                        # sort by created_at desc
                        rooms_sorted = sorted(rooms, key=lambda x: x.get("created_at",""), reverse=True)
                        # keep 5 most recent
                        to_keep_ids = set([r.get("id") for r in rooms_sorted[:5]])
                        new_rooms = []
                        for r in data.get("rooms", []):
                            if r.get("posted_by_phone") == phone and r.get("id") not in to_keep_ids:
                                # if this room was created after agent activation, delete it
                                # For simplicity, delete any beyond 5
                                if len([x for x in new_rooms if x.get("posted_by_phone")==phone]) >=5:
                                    # this is extra - deplete
                                    continue
                                # Actually we rebuild keeping only 5
                                pass
                            new_rooms.append(r)
                        # Re-filter to keep only 5 for this user
                        # Build final list
                        other_rooms = [r for r in data.get("rooms", []) if r.get("posted_by_phone") != phone]
                        user_rooms_keep = sorted([r for r in data.get("rooms", []) if r.get("posted_by_phone")==phone], key=lambda x: x.get("created_at",""), reverse=True)[:5]
                        data["rooms"] = other_rooms + user_rooms_keep
                        u["agent_package"] = None
                        u["agent_package_until"] = None
                        u["agent_active_limit"] = 0
                        modified = True
                except Exception as e:
                    pass
        # FREE SLOT RESET EVERY 30 DAYS FOREVER
        last_reset_str = u.get("last_post_reset")
        if last_reset_str:
            try:
                last_reset = datetime.fromisoformat(last_reset_str)
                if now >= last_reset + timedelta(days=30):
                    u["monthly_free_posts"] = 0
                    u["last_post_reset"] = now.isoformat()
                    modified = True
            except Exception:
                u["last_post_reset"] = now.isoformat()
                u["monthly_free_posts"] = 0
                modified = True
        else:
            u["last_post_reset"] = now.isoformat()
            u.setdefault("monthly_free_posts", 0)
            modified = True

    # Car hire expiry - 30 days auto delete or deactivate
    valid_drivers = []
    for d in data.get("car_hire", []):
        exp_str = d.get("expires_at")
        if exp_str:
            try:
                if now <= datetime.fromisoformat(exp_str):
                    valid_drivers.append(d)
                else:
                    modified = True
            except:
                valid_drivers.append(d)
        else:
            valid_drivers.append(d)
    data["car_hire"] = valid_drivers

    if modified:
        save_persistent_db(data)
    return data


def load_persistent_db():
    default_db = {"rooms": [], "student_rooms": [], "requests": [], "student_requests": [], "houses_sale": [], "car_hire": [], "users": [], "banned_phones": [], "logged_out_phones": [], "pending_payments": [], "approved_payments": [], "verified_references": [], "activity_logs": [], "device_slots": {}, "hot_deals": [None, None, None]}
    # ===== CLEAN MODE: If RESET_NOW file exists or DB has old data, wipe it =====
    # For this version, we ALWAYS start clean as requested
    try:
        if os.path.exists(DB_FILE):
            # Read existing to check if it has data - if yes, reset to clean
            with open(DB_FILE, "r") as f:
                existing = json.load(f)
            has_data = any(len(existing.get(k, []))>0 for k in ["rooms","student_rooms","houses_sale","car_hire","requests","pending_payments","approved_payments","users"])
            if has_data:
                # Reset to clean
                with open(DB_FILE, "w") as out:
                    json.dump(default_db, out, indent=4)
                # Clean session files
                for fp in [SESSION_FILE, SEEN_FILE]:
                    if os.path.exists(fp):
                        try: os.remove(fp)
                        except: pass
                return default_db
    except:
        pass

    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: json.dump(default_db, f, indent=4)
        return default_db
    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
            for k,v in default_db.items(): data.setdefault(k,v)
            for u in data.get("users", []):
                u.setdefault("is_vip", False); u.setdefault("vip_until", None); u.setdefault("paid_house_slots", 0); u.setdefault("monthly_free_posts", 0); u.setdefault("last_post_reset", datetime.now().isoformat()); u.setdefault("agent_package", None); u.setdefault("agent_package_until", None); u.setdefault("agent_active_limit", 0)
            return cleanup_expired_items(data)
    except Exception: return default_db

def load_session_persistence():
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE,"r") as f: return json.load(f)
        except: return None
    return None

def save_session_persistence(name, phone, role):
    try:
        with open(SESSION_FILE,"w") as f: json.dump({"name":name,"phone":phone,"role":role,"saved_at":datetime.now().isoformat()},f)
    except Exception: pass

def clear_session_persistence():
    try:
        if os.path.exists(SESSION_FILE): os.remove(SESSION_FILE)
    except: pass

def load_seen_ids():
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE,"r") as f: return set(json.load(f))
        except: return set()
    return set()

def save_seen_ids(seen_set):
    try:
        with open(SEEN_FILE,"w") as f: json.dump(list(seen_set),f)
    except: pass

def log_activity(action, details):
    log_entry = {"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "user_name": st.session_state.get("user_name", "System"), "user_phone": st.session_state.get("user_phone", "N/A"), "action": action, "details": details}
    st.session_state.db.setdefault("activity_logs", []).append(log_entry)
    save_persistent_db(st.session_state.db)

if "db" not in st.session_state: st.session_state.db = load_persistent_db()
if "navigation" not in st.session_state: st.session_state.navigation = "Home"
if "seen_payment_ids" not in st.session_state: st.session_state.seen_payment_ids = load_seen_ids()
if "editing_item_type" not in st.session_state: st.session_state.editing_item_type = None
if "editing_item_id" not in st.session_state: st.session_state.editing_item_id = None
if "filter_home_loc" not in st.session_state: st.session_state.filter_home_loc = "All Locations"
if "filter_home_type" not in st.session_state: st.session_state.filter_home_type = "All Types"
if "filter_home_price" not in st.session_state: st.session_state.filter_home_price = "Any budget"
if "admin_authenticated" not in st.session_state: st.session_state.admin_authenticated = False
if "dashboard_opened_at" not in st.session_state: st.session_state.dashboard_opened_at = None

MUTARE_LOCATIONS = ["All Locations","Chikanga","Dangamvura","Greenside","Greenside Extensions","Chikomo","Bernwin","Bordervale","Zimunya","Mountain Rise","Sakubva","Westlea","Zimta","Natview","Fairbridge Park","Morningside","Darlington","Florida","CBD","Link Road","Murambi","Hobhouse","Gimboki","Fern Valley","Weirmouth","Near Mutare Polytechnic","Near Mutare State University","Yeovil","Acid","Palmerstone","World Bank"]
ROOM_TYPES = ["All Types","Single","Cottage","Backyard Cottages","Shared Apartment","Students Only","Lodging","Shared","Bedsitter","Full House","2 Rooms","3 Rooms","4 Rooms","5 Rooms"]
PROPERTY_TYPES_SALE = ["Residential House","Residential Stand / Land","Commercial Property","Agricultural Land / Plot"]
VEHICLE_TYPES = ["Pick up truck", "Lorry Truck"]
IMAGE_TYPES_ALLOWED = ["jpg", "jpeg", "png", "webp", "heic", "bmp"]

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "user_phone" not in st.session_state: st.session_state.user_phone = ""
if "user_role" not in st.session_state: st.session_state.user_role = "Tenant"

if not st.session_state.logged_in:
    sess = load_session_persistence()
    if sess:
        clean_phone = canonical_phone(sess.get("phone",""))
        # normalize banned/logged out lists to canonical for check
        banned_can = [canonical_phone(x) for x in st.session_state.db.get("banned_phones",[])]
        logged_can = [canonical_phone(x) for x in st.session_state.db.get("logged_out_phones",[])]
        if clean_phone and clean_phone not in banned_can and clean_phone not in logged_can:
            st.session_state.logged_in = True
            st.session_state.user_name = sess.get("name","")
            st.session_state.user_phone = clean_phone
            st.session_state.user_role = sess.get("role","Tenant")

def show_post_success_message(item_type, title, expiry_days, extra_info=""):
    if is_owner(): expiry_text = "10 YEARS - Unlimited"
    else:
        expiry_text = f"{expiry_days} days"
        if expiry_days >= 3650: expiry_text = "10 YEARS"
    st.balloons()
    st.markdown(f"""<div class="success-post-banner"><h3>✅ Success! {title} Posted!</h3><p><b>Your {item_type} is now LIVE on Mutare Room Finder!</b></p><p>⏰ Expires in: {expiry_text}</p><p>Manage your listing from Dashboard (private)<br>{extra_info}</p><p>🎉 Tenants will contact you via WhatsApp/Call directly!</p></div>""", unsafe_allow_html=True)

def validate_zw_phone(phone_str):
    clean_num = re.sub(r"\D", "", str(phone_str))
    return len(clean_num) >= 9 and len(clean_num) <= 13

def validate_ecocash_ref(ref_str):
    if not ref_str: return False
    pattern = r"^[A-Za-z0-9\.]{8,30}$"
    return re.match(pattern, ref_str.strip()) is not None

def format_wa_inquiry_link(phone_str, item_title, item_price, category="Room"):
    wa_clean = re.sub(r"\D", "", str(phone_str))
    if len(wa_clean) == 10 and wa_clean.startswith("0"): wa_clean = "263" + wa_clean[1:]
    raw_message = f"Hello! I am inquiring about your {category} listing titled '{item_title}' priced at ${item_price} on Mutare Room Finder. Is it still available?"
    return f"https://wa.me/{wa_clean}?text={urllib.parse.quote(raw_message)}"

def render_middleman_banner():
    with st.container(border=True):
        st.caption("🛡️ PREMIUM TRUSTED SERVICE - GELLA ENTERPRISES")
        st.subheader("Secure a Room Safely with Our Trusted Middleman Service")
        st.write("Don't risk your money! For **$35 USD**, our team personally verifies landlords & secures your payment.")
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown("🛡️ **Scam Protection**"); st.caption("Admin verifies all parties.")
        with m2: st.markdown("✅ **Verified**"); st.caption("Real verified landlords only.")
        with m3: st.markdown("🔒 **Safer**"); st.caption("Via Gella Enterprises Pvt Ltd Pvt.")
        with m4: st.markdown("⚡ **Faster**"); st.caption("Close deals faster.")
        st.divider()
        c1, c2, c3 = st.columns([1,1,1])
        with c1: st.metric("Middleman Fee", "$35 USD", "100% Safe")
        with c2: st.link_button("💬 WhatsApp: 071 218 1037", "https://wa.me/263712181037?text=Hello%20Admin,%20I%20need%20Middleman%20Service%20for%20a%20room", use_container_width=True, type="primary")
        with c3: st.link_button("📞 Call: 078 985 1813", "tel:0789851813", use_container_width=True)

def render_image_gallery(images_list, key_prefix, compact=False):
    valid_imgs = [img for img in images_list if img]
    if not valid_imgs:
        st.markdown("""<div class="placeholder-house" style="height:180px !important;"><div class="ph-icon" style="font-size:36px !important;">🏠</div><div class="ph-text">NO PHOTO AVAILABLE</div></div>""", unsafe_allow_html=True)
        return
    # Initialize slide index in session state
    slide_key = f"slide_idx_{key_prefix}"
    if slide_key not in st.session_state:
        st.session_state[slide_key] = 0
    # Clamp index
    if st.session_state[slide_key] >= len(valid_imgs):
        st.session_state[slide_key] = 0
    if st.session_state[slide_key] < 0:
        st.session_state[slide_key] = len(valid_imgs)-1
    
    current_idx = st.session_state[slide_key]
    
    # Compact mode for car hire - small picture like rooms (260px max, not huge)
    if compact:
        # Small card style - max 260px height
        c1, c2, c3 = st.columns([0.15, 0.7, 0.15])
        with c1:
            if st.button("◀", key=f"prev_{key_prefix}", use_container_width=True):
                st.session_state[slide_key] = (current_idx - 1) % len(valid_imgs)
                st.rerun()
        with c2:
            st.image(valid_imgs[current_idx], use_container_width=True)
            st.caption(f"📸 {current_idx+1}/{len(valid_imgs)} - Vehicle Photo")
        with c3:
            if st.button("▶", key=f"next_{key_prefix}", use_container_width=True):
                st.session_state[slide_key] = (current_idx + 1) % len(valid_imgs)
                st.rerun()
        # Thumbnails small
        if len(valid_imgs) > 1:
            tcols = st.columns(min(len(valid_imgs), 5))
            for idx, img in enumerate(valid_imgs[:5]):
                with tcols[idx]:
                    if idx == current_idx:
                        st.markdown('<div style="border:2px solid #00FF88; border-radius:8px; padding:2px;">', unsafe_allow_html=True)
                        st.image(img, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    else:
                        if st.button(f"View {idx+1}", key=f"thumb_{key_prefix}_{idx}", use_container_width=True):
                            st.session_state[slide_key] = idx
                            st.rerun()
        return
    
    # Normal gallery for houses/rooms - SWIPE SLIDE BUTTONS
    if len(valid_imgs) == 1:
        st.image(valid_imgs[0], use_container_width=True)
    else:
        # Slide with prev/next buttons
        c_prev, c_main, c_next = st.columns([0.12, 0.76, 0.12])
        with c_prev:
            if st.button("◀", key=f"prev_{key_prefix}", use_container_width=True, help="Previous photo - swipe"):
                st.session_state[slide_key] = (current_idx - 1) % len(valid_imgs)
                st.rerun()
        with c_main:
            st.image(valid_imgs[current_idx], use_container_width=True)
            st.markdown(f"<p style='text-align:center; font-weight:700; font-size:12px; color:#0F172A; margin:4px 0;'>📸 Photo {current_idx+1} of {len(valid_imgs)} - Swipe ◀ ▶ to see more</p>", unsafe_allow_html=True)
        with c_next:
            if st.button("▶", key=f"next_{key_prefix}", use_container_width=True, help="Next photo - swipe"):
                st.session_state[slide_key] = (current_idx + 1) % len(valid_imgs)
                st.rerun()
        # Dots indicator
        dots = "".join(["🟢 " if i==current_idx else "⚪ " for i in range(len(valid_imgs))])
        st.markdown(f"<p style='text-align:center; font-size:14px; margin:2px 0;'>{dots}</p>", unsafe_allow_html=True)
        # Thumbnail row for quick jump
        if len(valid_imgs) > 1:
            thumb_cols = st.columns(min(len(valid_imgs), 6))
            for idx, img in enumerate(valid_imgs[:6]):
                with thumb_cols[idx]:
                    border = "2px solid #3B82F6" if idx==current_idx else "1px solid #E2E8F0"
                    st.markdown(f'<div style="border:{border}; border-radius:8px; padding:2px;">', unsafe_allow_html=True)
                    st.image(img, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    if st.button(f"{idx+1}", key=f"dot_{key_prefix}_{idx}", use_container_width=True):
                        st.session_state[slide_key] = idx
                        st.rerun()

def canonical_phone(p):
    """Normalize Zimbabwe numbers: 2637... -> 07... , keep canonical 07 form for matching"""
    d = re.sub(r"\D", "", str(p))
    if not d:
        return d
    # Handle 263 prefix
    if d.startswith("263") and len(d) >= 11:
        d = "0" + d[3:]
    # Handle leading 0 already
    if len(d) == 9:  # e.g. 789851813 -> 0789851813
        d = "0" + d
    return d

def is_admin_phone(phone):
    canon = canonical_phone(phone)
    raw = re.sub(r"\D", "", str(phone))
    admin_nums = ["0789851813", "0712181037", "263789851813", "263712181037", "789851813", "712181037"]
    admin_canon = [canonical_phone(x) for x in admin_nums]
    return canon in admin_canon or raw in admin_nums or raw in admin_canon

def is_admin_name(name):
    n = name.strip().lower()
    return "lewis" in n and "kajayi" in n

def is_owner():
    if not st.session_state.logged_in: 
        return False
    # Strict admin: only Lewis Kajayi with admin phones
    if not is_admin_name(st.session_state.user_name):
        return False
    if not is_admin_phone(st.session_state.user_phone):
        return False
    return True

def register_user_session(name, phone, role):
    clean_phone_raw = re.sub(r"\D", "", str(phone))
    canon = canonical_phone(phone)
    input_name = name.strip()
    input_name_lower = input_name.lower()
    if not canon:
        return False, "❌ Invalid phone number"
    # Banned check
    banned = st.session_state.db.get("banned_phones", [])
    banned_canonical = [canonical_phone(b) for b in banned]
    if clean_phone_raw in banned or canon in banned or canon in banned_canonical:
        return False, "❌ Account Banned - Contact Admin 078 985 1813"
    
    # STRICT: One phone = One account - name must match exactly (case-insensitive)
    users = st.session_state.db.get("users", [])
    existing_user = None
    for u in users:
        up = u.get("phone","")
        if canonical_phone(up) == canon or re.sub(r"\D","",up) == clean_phone_raw or re.sub(r"\D","",up) == canon or up == canon:
            existing_user = u
            break
    
    if existing_user:
        stored_name = existing_user.get("name","").strip()
        stored_name_lower = stored_name.lower()
        if stored_name_lower != input_name_lower:
            return False, f"❌ {canon} belongs to another user. You entered {input_name}."
        # Name matches (case-insensitive) - allow re-login
        existing_user["phone"] = canon
        existing_user["last_login"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        existing_user["role"] = role
        existing_user.setdefault("is_vip", False)
        existing_user.setdefault("vip_until", None)
        existing_user.setdefault("paid_house_slots", 0)
        existing_user.setdefault("monthly_free_posts", 0)
        existing_user.setdefault("last_post_reset", datetime.now().isoformat())
        existing_user.setdefault("agent_package", None)
        existing_user.setdefault("agent_package_until", None)
        existing_user.setdefault("agent_active_limit", 0)
        # Clear logged_out
        lo = st.session_state.db.get("logged_out_phones", [])
        st.session_state.db["logged_out_phones"] = [x for x in lo if canonical_phone(x) != canon and re.sub(r"\D","",x) != clean_phone_raw]
        save_persistent_db(st.session_state.db)
        save_session_persistence(stored_name, canon, role)  # Keep original stored name casing
        log_activity("User Re-Login", f"User {stored_name} ({canon}) re-logged in as {role} - strict name match.")
        return True, "Success Re-Login"
    else:
        # New account - if admin phone used with different name, show brief belongs to
        if is_admin_phone(canon) and not is_admin_name(input_name):
            return False, f"❌ {canon} belongs to another user. You entered {input_name}."
        # Check if name already exists with different phone (optional - prevent duplicate names with different phones? Allow same name different phone? We allow but warn)
        # Create new user
        users.append({"name": input_name, "phone": canon, "role": role, "first_login": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), "last_login": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"), "is_vip": False, "vip_until": None, "paid_house_slots": 0, "monthly_free_posts": 0, "last_post_reset": datetime.now().isoformat(), "agent_package": None, "agent_package_until": None, "agent_active_limit": 0})
        device_id = get_device_id()
        device_slots = st.session_state.db.setdefault("device_slots", {})
        device_slots[device_id] = {"bound_phone": canon, "registered_at": datetime.now().isoformat()}
        st.session_state.db["users"] = users
        # Clear logged_out
        lo = st.session_state.db.get("logged_out_phones", [])
        st.session_state.db["logged_out_phones"] = [x for x in lo if canonical_phone(x) != canon]
        save_persistent_db(st.session_state.db)
        save_session_persistence(input_name, canon, role)
        log_activity("User Login", f"New user {input_name} ({canon}) logged in as {role}.")
        return True, "Success"

def render_property_card(item, idx, category_type="Room", is_admin_view=False, show_countdown=False):
    is_featured = item.get("is_featured", False)
    is_rented = item.get("status") in ["Rented", "Taken"]
    status_badge = "🔴 MARKED AS TAKEN" if is_rented else "🟢 AVAILABLE"
    if is_rented and not is_admin_view: return
    with st.container(border=True):
        if is_featured: st.markdown('<div class="featured-badge">⭐ FEATURED LISTING</div>', unsafe_allow_html=True)
        if show_countdown:
            cd_str = format_countdown(item.get("expires_at") or item.get("featured_until"))
            if cd_str: st.markdown(f'<div class="countdown-badge">{cd_str}</div>', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        with col1: render_image_gallery(item.get("imgs", []), f"{category_type}_img_{idx}")
        with col2:
            st.subheader(f"{item.get('title', item.get('name', 'Property'))} `[{status_badge}]`")
            st.write(f"📍 **Location:** {item.get('loc', item.get('area', 'N/A'))} | 🏠 **Type:** {item.get('type', 'N/A')} | 💷 **Price:** ${item.get('price', item.get('rates', 'N/A'))}")
            st.write(f"💬 **WhatsApp:** `{item.get('contact_wa', item.get('phone_wa', 'N/A'))}` | 📞 **Direct Call:** `{item.get('contact_call', item.get('phone_call', 'N/A'))}`")
            st.write(f"📝 **Description:** {item.get('desc', 'N/A')}")
            if item.get("rules"): 
                st.markdown(f"""<div class="rules-card"><div class="rules-header">📜 Landlord Rules</div><div class="rules-text">{item['rules']}</div></div>""", unsafe_allow_html=True)
            b1, b2 = st.columns(2)
            with b1:
                wa_url = format_wa_inquiry_link(item.get("contact_wa", item.get("phone_wa", "")), item.get("title", item.get("name", "")), item.get("price", item.get("rates", "")), category=category_type)
                st.link_button("💬 Chat on WhatsApp", wa_url, use_container_width=True)
            with b2: st.link_button("📞 Call Contact", f"tel:{item.get('contact_call', item.get('contact_wa', ''))}", use_container_width=True)

def render_hot_deal_card(deal, slot_index):
    with st.container(border=True):
        if not deal:
            st.markdown(f"### 🔥 Hot Deal Slot #{slot_index + 1} Available")
            st.info("Promote your listing on this premium top banner! Pay $4 for 7 days feature.")
            st.link_button("🚀 Feature Your Deal Here ($4 USD)", "#", use_container_width=True)
            return
        st.markdown('<div class="hot-deal-badge">🔥 HOT DEAL IN MUTARE TODAY</div>', unsafe_allow_html=True)
        st.subheader(f"{deal.get('title')} - ${deal.get('price')}/mo")
        render_image_gallery(deal.get("imgs", []), f"hot_deal_big_img_{slot_index}")
        st.markdown(f"📍 **Location:** {deal.get('loc')} | 🏠 **Type:** {deal.get('type')}")
        st.write(f"📝 **Description:** {deal.get('desc', 'N/A')}")
        if deal.get("rules"): 
            st.markdown(f"""<div class="rules-card"><div class="rules-header">📜 Landlord Rules</div><div class="rules-text">{deal.get('rules')}</div></div>""", unsafe_allow_html=True)
        hb1, hb2 = st.columns(2)
        with hb1:
            wa_url = format_wa_inquiry_link(deal.get("contact_wa", ""), deal.get("title", ""), deal.get("price", ""), category="HOT DEAL")
            st.link_button("💬 WhatsApp Owner", wa_url, use_container_width=True)
        with hb2: st.link_button("📞 Call Now", f"tel:{deal.get('contact_call', deal.get('contact_wa', ''))}", use_container_width=True)


def activate_payment_package(payment_record):
    pkg_name = payment_record.get("package_name", "")
    duration = payment_record.get("package_days", 30)
    feature_target = payment_record.get("feature_target")
    acc_phone = payment_record.get("account_phone")
    now_dt = datetime.now()
    if "Basic Listing" in pkg_name or "House / Stand Basic Listing Fee" in pkg_name:
        for u in st.session_state.db.get("users", []):
            if u.get("phone") == acc_phone:
                u["paid_house_slots"] = u.get("paid_house_slots", 0) + 1
    elif "Agent / House For Sale VIP" in pkg_name or "VIP (30 Days Unlimited Listing)" in pkg_name:
        for u in st.session_state.db.get("users", []):
            if u.get("phone") == acc_phone:
                u["is_vip"] = True
                u["vip_until"] = (now_dt + timedelta(days=30)).isoformat()
    elif "Rooms to Rent Agent" in pkg_name and "Agency" not in pkg_name:
        for u in st.session_state.db.get("users", []):
            if u.get("phone") == acc_phone:
                u["agent_package"] = "Agent ($10/mo)"
                u["agent_package_until"] = (now_dt + timedelta(days=30)).isoformat()
                u["agent_active_limit"] = 25
                # Extend existing rooms to 30 days
                for r in st.session_state.db.get("rooms", []):
                    if r.get("posted_by_phone") == acc_phone:
                        r["expires_at"] = (now_dt + timedelta(days=30)).isoformat()
    elif "Rooms to Rent Agency/Business" in pkg_name or "Agency ($25" in pkg_name or "Unlimited" in pkg_name:
        for u in st.session_state.db.get("users", []):
            if u.get("phone") == acc_phone:
                u["agent_package"] = "Agency ($25/mo) Unlimited"
                u["agent_package_until"] = (now_dt + timedelta(days=30)).isoformat()
                u["agent_active_limit"] = 99999
                for r in st.session_state.db.get("rooms", []):
                    if r.get("posted_by_phone") == acc_phone:
                        r["expires_at"] = (now_dt + timedelta(days=30)).isoformat()
    elif "HOT DEAL TOP SLOT" in pkg_name:
        hot_deals = st.session_state.db.get("hot_deals", [None, None, None])
        target_slot = payment_record.get("hot_deal_slot_index", 0)
        if feature_target and isinstance(feature_target, dict):
            item_id = feature_target.get("id")
            db_key = feature_target.get("db_key", "rooms")
            target_item = next((item for item in st.session_state.db.get(db_key, []) if item.get("id") == item_id), None)
            if target_item:
                hot_deal_data = {
                    "id": target_item.get("id"),
                    "title": target_item.get("title", target_item.get("name")),
                    "price": target_item.get("price", target_item.get("rates")),
                    "loc": target_item.get("loc", target_item.get("area")),
                    "type": target_item.get("type", "Standard"),
                    "imgs": target_item.get("imgs", []),
                    "desc": target_item.get("desc", ""),
                    "rules": target_item.get("rules", ""),
                    "contact_wa": target_item.get("contact_wa", target_item.get("phone_wa")),
                    "contact_call": target_item.get("contact_call", target_item.get("phone_call")),
                    "expires_at": (now_dt + timedelta(days=7)).isoformat(),
                    "_origin_db_key": db_key,
                    "_origin_featured_days": 7
                }
                if 0 <= target_slot < 3:
                    hot_deals[target_slot] = hot_deal_data
                st.session_state.db["hot_deals"] = hot_deals
                # Mark original as hot deal with 7 days
                target_item["is_hot_deal"] = True
                target_item["featured_days"] = 7
                target_item["featured_until"] = (now_dt + timedelta(days=7)).isoformat()
                target_item["is_featured"] = True
    if feature_target and isinstance(feature_target, dict) and "HOT DEAL" not in pkg_name:
        db_key = feature_target.get("db_key")
        item_id = feature_target.get("id")
        if db_key == "car_hire":
            for driver in st.session_state.db.get("car_hire", []):
                if driver.get("id") == item_id:
                    driver["is_approved"] = True
                    driver["approved_until"] = (now_dt + timedelta(days=duration)).isoformat()
        elif db_key in st.session_state.db:
            for item in st.session_state.db.get(db_key, []):
                if item.get("id") == item_id:
                    item["is_featured"] = True
                    item["featured_until"] = (now_dt + timedelta(days=duration)).isoformat()
                    item["featured_days"] = duration
                    # For 7-day featured, keep expires same as featured (will be converted to 21d after)
                    # For 30-day featured, expires = 30d then will be removed
                    if duration == 7:
                        item["expires_at"] = (now_dt + timedelta(days=7)).isoformat()
                    else:
                        item["expires_at"] = (now_dt + timedelta(days=duration)).isoformat()
    log_activity("Package Activated", f"Unlocked {pkg_name} for ref {payment_record.get('reference')}.")



def deplete_package(payment_record):
    feature_target = payment_record.get("feature_target")
    acc_phone = payment_record.get("account_phone")
    pkg_name = payment_record.get("package_name", "")
    now = datetime.now()
    if feature_target and isinstance(feature_target, dict):
        db_key = feature_target.get("db_key")
        item_id = feature_target.get("id")
        if db_key == "car_hire":
            for d in st.session_state.db.get("car_hire", []):
                if d.get("id") == item_id:
                    d["is_approved"] = False
        elif db_key in st.session_state.db:
            for item in st.session_state.db.get(db_key, []):
                if item.get("id") == item_id:
                    if "HOT DEAL" in pkg_name or item.get("featured_days") == 7:
                        # Hot deal or 7-day featured -> shuffle to normal 21 days
                        item["is_featured"] = False
                        item["featured_until"] = None
                        item["featured_days"] = None
                        item["is_hot_deal"] = False
                        item["expires_at"] = (now + timedelta(days=21)).isoformat()
                    else:
                        # 30-day featured -> remove completely
                        if item.get("featured_days", 0) >= 30:
                            # Will be removed by marking expired
                            item["expires_at"] = (now - timedelta(days=1)).isoformat()
                        else:
                            item["is_featured"] = False
                            item["featured_until"] = None
                            item["featured_days"] = None
                            item["expires_at"] = (now + timedelta(days=21)).isoformat()
        if "HOT DEAL" in pkg_name:
            for i in range(len(st.session_state.db.get("hot_deals", []))):
                hd = st.session_state.db["hot_deals"][i]
                if hd and hd.get("id") == item_id:
                    st.session_state.db["hot_deals"][i] = None
                    # Also reshuffle original to 21 days
                    for key in ["rooms", "student_rooms", "houses_sale"]:
                        for it in st.session_state.db.get(key, []):
                            if it.get("id") == item_id:
                                it["is_featured"] = False
                                it["featured_until"] = None
                                it["is_hot_deal"] = False
                                it["expires_at"] = (now + timedelta(days=21)).isoformat()
    for u in st.session_state.db.get("users", []):
        if u.get("phone") == acc_phone:
            if "VIP" in pkg_name or "Agent / House For Sale" in pkg_name:
                u["is_vip"] = False
                u["vip_until"] = None
            if "Rooms to Rent Agent" in pkg_name or "Agency/Business" in pkg_name or "Unlimited" in pkg_name:
                # Expire agent package - keep only 5 rooms
                other_rooms = [r for r in st.session_state.db.get("rooms", []) if r.get("posted_by_phone") != acc_phone]
                user_rooms_sorted = sorted([r for r in st.session_state.db.get("rooms", []) if r.get("posted_by_phone")==acc_phone], key=lambda x: x.get("created_at",""), reverse=True)
                user_keep = user_rooms_sorted[:5]
                st.session_state.db["rooms"] = other_rooms + user_keep
                u["agent_package"] = None
                u["agent_package_until"] = None
                u["agent_active_limit"] = 0
    payment_record["status"] = "Depleted by Admin"
    payment_record["depleted_at"] = now.isoformat()
    save_persistent_db(st.session_state.db)


if not st.session_state.logged_in:
    st.markdown('''
    <style>
    [data-testid="stAppViewContainer"] {
        background: 
            radial-gradient(ellipse at 0% 0%, rgba(0,255,136,0.55) 0%, transparent 42%),
            radial-gradient(ellipse at 95% 25%, rgba(0,255,136,0.45) 0%, transparent 40%),
            radial-gradient(ellipse at 30% 50%, rgba(0,140,255,0.85) 0%, transparent 60%),
            radial-gradient(ellipse at 85% 80%, rgba(0,80,255,0.65) 0%, transparent 55%),
            linear-gradient(135deg, #020617 0%, #0A1A4A 22%, #0E2F8A 48%, #0B4FB8 74%, #0A6ED8 100%) !important;
        background-attachment: fixed !important;
    }
    /* WHITE CARDS LITTLE TRANSPARENT BLEND - NOT HEAVY */
    [data-testid="stVerticalBlockBorderWrapper"], div[data-testid="stExpander"], div[data-testid="stForm"] {
        background: rgba(255,255,255,0.88) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        border-radius: 16px !important; 
        border: 1px solid rgba(255,255,255,0.65) !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.6) !important;
    }
    /* INPUTS LITTLE TRANSPARENT */
    div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea, div[data-testid="stNumberInput"] input {
        background: rgba(255,255,255,0.88) !important;
        backdrop-filter: blur(8px) !important;
        border: 1.5px solid rgba(203,213,225,0.9) !important;
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important;
    }
    
/* ===== FINAL FIX: ALL UPLOAD BUTTONS TEXT WHITE - HIGH VISIBILITY ===== */
div[data-testid="stFileUploader"] button,
div[data-testid="stFileUploader"] button *,
div[data-testid="stFileUploader"] [data-testid="stBaseButton-secondary"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    background: #0F172A !important;
    font-weight: 800 !important;
    opacity: 1 !important;
    visibility: visible !important;
}
div[data-testid="stFileUploader"] button p,
div[data-testid="stFileUploader"] button span,
div[data-testid="stFileUploader"] button div {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* Browse files button specific */
div[data-testid="stFileUploader"] section button {
    background: #0F172A !important;
    color: #FFFFFF !important;
    border: 1.5px solid #FFFFFF !important;
}
div[data-testid="stFileUploader"] section button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
/* The file cards themselves */
div[data-testid="stFileUploader"] section div[data-testid="stFileUploaderFile"] {
    background: #FFFFFF !important;
}
div[data-testid="stFileUploader"] section div[data-testid="stFileUploaderFile"] * {
    color: #0F172A !important;
}
/* WHY TRUST US CARDS - BLUE TRANSPARENT LIKE GELLA */
.gella-footer-fixed div[style*="background:rgba(255,255,255,0.14)"] {
    background: rgba(15,23,42,0.55) !important;
    border: 1.5px solid rgba(0,217,255,0.45) !important;
    backdrop-filter: blur(12px) !important;
}
/* Remove grey/blue/black solid backgrounds */
div[style*="background:rgba(255,255,255,0.14)"][style*="border-radius:12px"] {
    background: rgba(59,130,246,0.75) !important;
    border: 1.5px solid rgba(0,217,255,0.40) !important;
}
/* Login note white */
div[data-testid="stAppViewContainer"] p[style*="One phone number"] {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

</style>
    ''', unsafe_allow_html=True)
    
    # BIG ATTRACTIVE WELCOME BANNER
    st.markdown('''
    <div style="text-align:center; padding:32px 16px 20px 16px;">
        <h1 style="color:#FFFFFF !important; font-weight:900; font-size:42px; letter-spacing:-0.5px; margin:0; text-shadow:0 0 30px rgba(0,217,255,0.6), 0 4px 24px rgba(0,0,0,0.5); line-height:1.1;">
            🏠 Welcome to<br><span style="background:linear-gradient(135deg, #00FF88 0%, #00D9FF 50%, #FFFFFF 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; filter:drop-shadow(0 0 20px rgba(0,255,136,0.5));">Mutare Room Finder</span>
        </h1>
        <p style="font-size:16px; color:#DBEAFE; font-weight:600; margin:12px 0 0 0; text-shadow:0 2px 8px rgba(0,0,0,0.3);">Find your next home or post your available space in seconds.</p>
        <div style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap; margin-top:18px;">
            <span style="background:rgba(0,255,136,0.20); border:1.5px solid rgba(0,255,136,0.45); color:#00FF88; padding:7px 16px; border-radius:20px; font-size:12px; font-weight:800; backdrop-filter:blur(10px); box-shadow:0 2px 10px rgba(0,255,136,0.2);">🔒 Verified Landlords</span>
            <span style="background:rgba(0,217,255,0.20); border:1.5px solid rgba(0,217,255,0.45); color:#00D9FF; padding:7px 16px; border-radius:20px; font-size:12px; font-weight:800; backdrop-filter:blur(10px); box-shadow:0 2px 10px rgba(0,217,255,0.2);">⚡ Instant WhatsApp Connect</span>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([0.8, 2.4, 0.8])
    with col2:
        with st.container(border=True):
            st.markdown("<h3 style='color:#0F172A !important; text-align:center; font-weight:900; margin:0;'>🔑 Quick Login / Sign Up</h3><p style='color:#FFFFFF; font-size:11px; font-weight:700; text-align:center; margin:4px 0 0 0; text-shadow:0 1px 3px rgba(0,0,0,0.5);'>One phone number = One account - same name can re-login easily</p>", unsafe_allow_html=True)
            st.write("")
            role_choice = st.radio("SELECT ACCOUNT TYPE *", ["Tenant (Browse & Request Rooms)","Landlord (Post & Browse Rooms)"], horizontal=False)
            name_input = st.text_input("FULL NAME *", value="", placeholder="e.g. John Doe")
            phone_input = st.text_input("PHONE NUMBER (10 DIGITS E.G. 0781234567) *", value="", placeholder="e.g. 0771234567")
            if st.button("Start Browsing Now ✨", use_container_width=True, type="primary"):
                clean_phone = re.sub(r"\D", "", phone_input)
                assigned_role = "Landlord" if "Landlord" in role_choice else "Tenant"
                if not name_input.strip(): st.error("⚠️ Please enter your Full Name.")
                elif not validate_zw_phone(phone_input): st.error("❌ Invalid Phone Number! Must be 9-13 digits.")
                else:
                    success, msg = register_user_session(name_input.strip(), clean_phone, assigned_role)
                    if not success:
                        # Brief message showing name and number
                        st.markdown(f'<div style="background:#FEF2F2; border:1px solid #FECACA; color:#991B1B; padding:10px; border-radius:8px; font-weight:700;">{msg}<br><small>Attempt: {name_input.strip()} ({phone_input})</small></div>', unsafe_allow_html=True)
                    else:
                        st.session_state.logged_in = True; st.session_state.user_name = name_input.strip(); st.session_state.user_phone = clean_phone; st.session_state.user_role = assigned_role; st.rerun()
            st.markdown("---")
            # WHY US - 3 CARDS PRESENTABLE VISIBLE NO WHITE - FC26 GLASS
            st.markdown('''
            <div style="text-align:center; background:rgba(15,23,42,0.88); border:2px solid #FACC15; border-radius:16px; padding:18px; margin-bottom:14px; box-shadow:0 8px 24px rgba(59,130,246,0.35); backdrop-filter:blur(14px); background: rgba(59,130,246,0.25) !important; border:1.5px solid rgba(255,255,255,0.35) !important;">
                <p style="color:#FFFFFF !important; font-size:16px; font-weight:900; background: linear-gradient(135deg, #3B82F6 0%, #1E40AF 50%, #1E3A8A 100%) !important; padding:10px 24px; border-radius:12px; border:1.5px solid rgba(255,255,255,0.35); display:inline-block; margin:0; letter-spacing:0.5px; -webkit-text-fill-color:#FFFFFF !important; box-shadow:0 4px 14px rgba(59,130,246,0.45); text-transform:uppercase;">🌟 WHY 1000+ USERS TRUST US?</p>
                <div style="display:flex; justify-content:space-between; gap:10px; text-align:center; margin-top:16px;">
                    <div style="flex:1; background: linear-gradient(135deg, rgba(59,130,246,0.85) 0%, rgba(30,58,138,0.90) 100%); backdrop-filter:blur(12px); border-radius:12px; padding:14px 8px; border:1.5px solid rgba(255,255,255,0.35),136,0.45); box-shadow:0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.15);">
                        <p style="margin:0; font-size:28px; filter:drop-shadow(0 2px 6px rgba(0,255,136,0.4));">🏠</p>
                        <p style="margin:8px 0 0 0; color:#FFFFFF !important; font-size:12px; font-weight:800; line-height:1.3;">Chikanga to CBD</p>
                        <p style="margin:2px 0 0 0; color:#00FF88 !important; font-size:11px; font-weight:700;">25+ Locations</p>
                    </div>
                    <div style="flex:1; background: linear-gradient(135deg, rgba(59,130,246,0.80) 0%, rgba(30,64,175,0.85) 100%); backdrop-filter:blur(12px); border-radius:12px; padding:14px 8px; border:1.5px solid rgba(0,217,255,0.45); box-shadow:0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.15);">
                        <p style="margin:0; font-size:28px; filter:drop-shadow(0 2px 6px rgba(0,217,255,0.4));">⚡</p>
                        <p style="margin:8px 0 0 0; color:#FFFFFF !important; font-size:12px; font-weight:800; line-height:1.3;">Post in 30s</p>
                        <p style="margin:2px 0 0 0; color:#00D9FF !important; font-size:11px; font-weight:700;">Live Instantly</p>
                    </div>
                    <div style="flex:1; background: linear-gradient(135deg, rgba(59,130,246,0.80) 0%, rgba(30,64,175,0.85) 100%); backdrop-filter:blur(12px); border-radius:12px; padding:14px 8px; border:1.5px solid rgba(250,204,21,0.45); box-shadow:0 4px 12px rgba(0,0,0,0.15), inset 0 1px 0 rgba(255,255,255,0.15);">
                        <p style="margin:0; font-size:28px; filter:drop-shadow(0 2px 6px rgba(250,204,21,0.4));">💬</p>
                        <p style="margin:8px 0 0 0; color:#FFFFFF !important; font-size:12px; font-weight:800; line-height:1.3;">Direct WhatsApp</p>
                        <p style="margin:2px 0 0 0; color:#FACC15 !important; font-size:11px; font-weight:700;">No Middleman</p>
                    </div>
                </div>
            </div>
            ''', unsafe_allow_html=True)
            # GELLA VISIBLE - YELLOW BADGE
            st.markdown('''
            <div style="text-align:center; background:rgba(15,23,42,0.90) !important; border:2px solid #FACC15; border-radius:14px; padding:14px; box-shadow:0 4px 16px rgba(0,0,0,0.25);">
                <p style="color:#0F172A !important; font-size:15px; font-weight:900; background:#FEF9C3 !important; padding:9px 20px; border-radius:10px; border:2px solid #FACC15; display:inline-block; margin:0; letter-spacing:0.3px; -webkit-text-fill-color:#422006 !important; box-shadow:0 2px 10px rgba(250,204,21,0.4);">Gella Enterprises Pvt Ltd</p>
                <p style="color:#FEF08A !important; font-size:11px; font-weight:700; margin:10px 0 0 0; letter-spacing:0.5px;">Secure • Verified • Trusted Platform</p>
                <p style="color:#FDE68A !important; font-size:12px; font-weight:800; margin:8px 0 0 0;">© 2026 Mutare Room Finder. All Rights Reserved.</p>
            </div>
            ''', unsafe_allow_html=True)
    st.stop()


user_phone_clean = canonical_phone(st.session_state.user_phone)
if user_phone_clean in st.session_state.db.get("banned_phones", []):
    st.error("⛔ Access Denied: Your account has been banned.")
    if st.button("Logout"): clear_session_persistence(); st.session_state.logged_in = False; st.session_state.admin_authenticated=False; st.rerun()
    st.stop()
if user_phone_clean in st.session_state.db.get("logged_out_phones", []):
    st.warning("⚠️ Session Terminated: Logged out by Admin.")
    st.session_state.db["logged_out_phones"].remove(user_phone_clean); save_persistent_db(st.session_state.db)
    clear_session_persistence(); st.session_state.logged_in = False; st.session_state.admin_authenticated=False; st.rerun()

st.sidebar.markdown("## 🏠 **Mutare Room Finder**")
role_badge = "👥 TENANT" if st.session_state.user_role == "Tenant" else "🏠 LANDLORD"
badge_color = "#00D9FF" if st.session_state.user_role == "Tenant" else "#00FF88"
if is_owner(): 
    st.sidebar.markdown(f"""<div style="background:rgba(15,23,42,0.92) !important; border:2px solid #FACC15; border-radius:14px; padding:14px; text-align:center; box-shadow:0 6px 18px rgba(0,0,0,0.25);"><p style="color:#422006 !important; font-weight:900; font-size:15px; margin:0; background:#FEF9C3; padding:6px 14px; border-radius:10px; display:inline-block; border:2px solid #FACC15; box-shadow:0 2px 8px rgba(250,204,21,0.4);">👑 Welcome Admin</p><p style="color:#FFFFFF !important; font-weight:800; font-size:14px; margin:10px 0 0 0;">{st.session_state.user_name}</p><p style="color:{badge_color} !important; font-weight:900; font-size:12px; margin:6px 0 0 0; background:rgba(255,255,255,0.15); padding:4px 10px; border-radius:20px; display:inline-block; border:1px solid {badge_color};">🏠 LANDLORD • ADMIN</p></div>""", unsafe_allow_html=True)
else: 
    st.sidebar.markdown(f"""<div style="background:rgba(15,23,42,0.90) !important; border:2px solid {badge_color}; border-radius:14px; padding:16px; text-align:center; box-shadow:0 6px 18px rgba(0,0,0,0.25); backdrop-filter:blur(12px);">
    <p style="color:#DBEAFE !important; font-weight:700; font-size:12px; margin:0; letter-spacing:1px;">👋 Welcome,</p>
    <p style="color:#FFFFFF !important; font-weight:900; font-size:17px; margin:6px 0 0 0; text-shadow:0 2px 8px rgba(0,0,0,0.3);">{st.session_state.user_name}</p>
    <div style="margin-top:10px; background:{badge_color}; padding:8px 16px; border-radius:20px; display:inline-block; box-shadow:0 4px 12px rgba(0,0,0,0.2);">
        <p style="color:#020617 !important; font-weight:900; font-size:13px; margin:0; letter-spacing:0.5px;">{role_badge}</p>
    </div>
    <p style="color:#94A3B8 !important; font-size:10px; font-weight:600; margin:8px 0 0 0;">{'Browsing Rooms' if st.session_state.user_role=='Tenant' else 'Posting & Managing Rooms'}</p>
    </div>""", unsafe_allow_html=True)

if st.sidebar.button("Logout 🚪", use_container_width=True):
    clear_session_persistence(); st.session_state.db.setdefault("logged_out_phones", []).append(user_phone_clean); save_persistent_db(st.session_state.db)
    st.session_state.logged_in = False; st.session_state.user_name = ""; st.session_state.user_phone = ""; st.session_state.user_role = "Tenant"; st.session_state.admin_authenticated=False; st.rerun()

st.sidebar.divider()
seen_ids = st.session_state.get("seen_payment_ids", set())
if is_owner():
    all_pending_ids = [p.get("id") for p in st.session_state.db.get("pending_payments", [])]
    unseen_admin = [pid for pid in all_pending_ids if pid not in seen_ids]
    admin_pending_count = len(unseen_admin)
else: admin_pending_count = 0
unseen_pending = [p for p in st.session_state.db.get("pending_payments", []) if p.get("account_phone") == user_phone_clean and p.get("id") not in seen_ids]
unseen_approved = [p for p in st.session_state.db.get("approved_payments", []) if p.get("account_phone") == user_phone_clean and p.get("id") not in seen_ids]
total_my_updates = len(unseen_pending) + len(unseen_approved)
dashboard_label = f"📊 Dashboard 🔔 ({total_my_updates})" if total_my_updates > 0 else "📊 Dashboard"
admin_label = f"👑 Admin Panel 🚨 ({admin_pending_count})" if is_owner() and admin_pending_count > 0 else "👑 Admin Panel"
menu_options = ["🏠 Home","🔍 Browse Rooms","🎓 Student Accommodation","🏘️ Houses for Sale","🚚 Car Hire (Transport)","📩 Requests (Wanted)","💳 Payments",dashboard_label,"📞 Contact"]
if st.session_state.user_role == "Landlord" or is_owner(): menu_options.insert(5, "➕ Post Room")
if is_owner(): menu_options.append(admin_label)


current_nav = st.session_state.navigation
nav_index = 0
for idx, opt in enumerate(menu_options):
    clean_opt = opt.split()[-1] if " " in opt else opt
    if current_nav in opt or opt in current_nav or clean_opt in current_nav: 
        nav_index = idx; break
    if opt.startswith(current_nav) or current_nav.startswith(opt.split()[-1]): 
        nav_index = idx; break
nav_choice = st.sidebar.radio("Menu Navigation:", menu_options, index=nav_index, key="main_nav_radio")
# Map emoji choice back to base tab name
if "🏠 Home" in nav_choice: selected_tab = "Home"
elif "🔍 Browse" in nav_choice: selected_tab = "Browse Rooms"
elif "🎓 Student" in nav_choice: selected_tab = "Student Accommodation"
elif "🏘️ Houses" in nav_choice: selected_tab = "Houses for Sale"
elif "🚚 Car Hire" in nav_choice: selected_tab = "Car Hire (Transport)"
elif "➕ Post Room" in nav_choice: selected_tab = "Post Room"
elif "📩 Requests" in nav_choice: selected_tab = "Requests (Wanted)"
elif "💳 Payments" in nav_choice: selected_tab = "Payments"
elif "📊 Dashboard" in nav_choice or "Dashboard" in nav_choice: selected_tab = "Dashboard"
elif "📞 Contact" in nav_choice: selected_tab = "Contact"
elif "👑 Admin Panel" in nav_choice or "Admin Panel" in nav_choice: selected_tab = "Admin Panel"
else: selected_tab = nav_choice
# Clean emoji for internal use
for base in ["Home","Browse Rooms","Student Accommodation","Houses for Sale","Car Hire (Transport)","Post Room","Requests (Wanted)","Payments","Dashboard","Contact","Admin Panel"]:
    if base in selected_tab:
        # keep Dashboard special
        if "Dashboard" in selected_tab: selected_tab="Dashboard"
        elif "Admin Panel" in selected_tab: selected_tab="Admin Panel"
        elif base!="Dashboard" and base!="Admin Panel" and base in nav_choice:
            selected_tab=base
        break
st.session_state.navigation = selected_tab

# FIXED: Only toast once per session to stop glitching
if "dashboard_toast_shown" not in st.session_state:
    st.session_state.dashboard_toast_shown = False
if total_my_updates > 0 and selected_tab!= "Dashboard" and not st.session_state.dashboard_toast_shown:
    st.toast(f"🔔 You have {total_my_updates} new package update(s)! Open Dashboard", icon="🔔")
    st.session_state.dashboard_toast_shown = True
if selected_tab == "Dashboard":
    # REMOVED: "User Dashboard-Private to You" title and caption as requested
    # REMOVED: All tabs under User Dashboard-Private to You (Verification, Messages, Standard Rooms, Manage, Student Housing, Houses for Sale)
    
    # Keep only landlord encouragement banner (previous banner restored)
    if st.session_state.user_role == "Landlord" or is_owner():
        st.markdown('''
        <div class="landlord-super-banner">
            <div style="text-align:center; margin-bottom:14px;">
                <p style="color:#0F172A !important; font-size:19px; font-weight:900; background:#FEF9C3 !important; padding:12px 26px; border-radius:14px; border:2.5px solid #FACC15; display:inline-block; margin:0; box-shadow:0 4px 16px rgba(250,204,21,0.5); -webkit-text-fill-color:#422006 !important;">💡 LANDLORD TIP - KEEP LISTINGS FRESH & FEATURED!</p>
            </div>
            <div style="background:rgba(255,255,255,0.14); border-radius:12px; padding:14px; border:1.5px solid rgba(255,255,255,0.25);">
                <p style="color:#FEF08A !important; font-weight:900; font-size:16px; margin:0; line-height:1.3;">✅ DELETE rooms marked as <span style="background:#EF4444; color:#FFFFFF; padding:2px 10px; border-radius:8px;">Rented / Taken</span> to keep your profile clean!</p>
                <p style="color:#FFFFFF !important; font-weight:800; font-size:15px; margin:12px 0 0 0; line-height:1.3;">⭐ FEATURE your rooms for <span style="background:#FEF9C3; color:#422006; padding:3px 12px; border-radius:10px; border:1.5px solid #FACC15; font-weight:900;">$2 / 7days or $5 / 30days</span> to get 5x more inquiries!</p>
                <p style="color:#00FF88 !important; font-size:13px; font-weight:700; margin:10px 0 0 0;">👉 Tenants trust clean profiles - Rented rooms left up scare them away!</p>
            </div>
            <div style="background:rgba(255,255,255,0.12); border-radius:12px; padding:14px; margin-top:14px; border:1.5px solid rgba(0,255,136,0.35);">
                <p style="color:#00FF88 !important; font-weight:900; font-size:14px; margin:0;">📢 ADVERTISING PACKAGES - BOOST ALL YOUR LISTINGS!</p>
                <div style="display:flex; flex-wrap:wrap; gap:8px; margin-top:10px;">
                    <span style="background:#0F172A; color:#FEF08A; padding:6px 12px; border-radius:18px; font-weight:800; font-size:12px; border:1.5px solid #FACC15;">🏠 Rooms: $2/7d • $5/30d • $10 agent/30 days (25 listings) • $20 Agency/Business (Unlimited listing)</span>
                    <span style="background:#1E3A8A; color:#BFDBFE; padding:6px 12px; border-radius:18px; font-weight:800; font-size:12px; border:1.5px solid #3B82F6;">🎓 Student: $3/7d • $6/30d • Top Visibility</span>
                    <span style="background:#14532D; color:#BBF7D0; padding:6px 12px; border-radius:18px; font-weight:800; font-size:12px; border:1.5px solid #16A34A;">🏘️ Houses Sale: 2 FREE • $3 Extra • $15 Featured 30d • $20 VIP Unlimited</span>
                    <span style="background:#422006; color:#FEF9C3; padding:6px 12px; border-radius:18px; font-weight:800; font-size:12px; border:1.5px solid #FACC15;">🔥 Hot Deal Top 3 Banner: $4/7d</span>
                </div>
                <p style="color:#DBEAFE !important; font-size:11px; font-weight:600; margin:8px 0 0 0;">All packages available in 💳 Payments tab → Select listing → Pay EcoCash → Admin approves in 1hr!</p>
            </div>
            <p style="color:#DBEAFE !important; font-size:12px; font-weight:600; margin:12px 0 0 0; text-align:center;">Use the Payments tab to feature your rooms</p>
        </div>
        ''', unsafe_allow_html=True)
        st.markdown('''
        <div class="feature-ad-banner" style="border-left-color:#00FF88 !important;">
            <div class="ad-title">🔔 LANDLORD ACTION - CHECK TENANT REQUESTS!</div>
            <p class="ad-main">📩 Tenants are posting what they NEED daily in <b>Requests (Wanted)</b> tab. Check it now to match your rooms & close deals faster!</p>
            <div class="ad-prices">
                <span class="price-pill green">💬 WhatsApp them directly</span>
                <span class="price-pill">📞 Call to secure tenant</span>
                <span class="price-pill blue">⚡ 21 days auto-delete - act fast!</span>
            </div>
            <p class="ad-footer">Pro Tip: Post rooms that match requests - tenants love landlords who listen!</p>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.info(f"👋 Welcome {st.session_state.user_name}! Use Browse tabs to find rooms. No private dashboard tabs needed.")

    # ===== DASHBOARD NOTIFICATION LIKE MESSAGE APP =====
    # When user opens Dashboard, badge shows 🔔 count, after opening it disappears
    # and only reappears when new payment/update arrives
    if "dashboard_opened_at" not in st.session_state:
        st.session_state.dashboard_opened_at = None
    # Reset timer every time we enter Dashboard
    if st.session_state.get("last_opened_tab") != "Dashboard":
        st.session_state.dashboard_opened_at = datetime.now()
        st.session_state.last_opened_tab = "Dashboard"
    if st.session_state.dashboard_opened_at is None:
        st.session_state.dashboard_opened_at = datetime.now()
    elapsed = (datetime.now() - st.session_state.dashboard_opened_at).total_seconds()
    if elapsed > 1.2:
        my_all_pays = [p.get("id") for p in st.session_state.db.get("pending_payments", []) + st.session_state.db.get("approved_payments", []) if p.get("account_phone") == user_phone_clean]
        if my_all_pays:
            st.session_state.seen_payment_ids.update(my_all_pays)
            # Clear badge after seen - will reappear only on new notification
            st.session_state.dashboard_toast_shown = False
            save_seen_ids(st.session_state.seen_payment_ids)
else:
    st.session_state.dashboard_opened_at = None

if selected_tab.startswith("Admin Panel") and is_owner():
    all_p = [p.get("id") for p in st.session_state.db.get("pending_payments", [])]
    if all_p:
        st.session_state.seen_payment_ids.update(all_p)
        save_seen_ids(st.session_state.seen_payment_ids)

if selected_tab == "Home":
    st.title("🏠 Find Your Perfect Room in Mutare")
    st.write("Browse available rooms across Chikanga, Greenside Extensions, Chikomo, Bernwin, Bordervale, Zimunya, CBD, and 25+ local locations.")
    st.subheader("🔥 HOT DEALS IN MUTARE TODAY - $4 / 7 Days")
    hot_deals = st.session_state.db.get("hot_deals", [None, None, None])
    hd_col1, hd_col2, hd_col3 = st.columns(3)
    with hd_col1: render_hot_deal_card(hot_deals[0], 0)
    with hd_col2: render_hot_deal_card(hot_deals[1], 1)
    with hd_col3: render_hot_deal_card(hot_deals[2], 2)
    st.divider()
    with st.container(border=True):
        st.markdown("#### 🔍 Search Location")
        search_col1, search_col2 = st.columns([3,1])
        with search_col1:
            loc_search_input = st.text_input("Search by location name", placeholder="e.g. Chikanga, CBD, Greenside...", key="home_loc_search_input", label_visibility="collapsed")
        with search_col2:
            search_btn = st.button("🔍 Search Location", use_container_width=True, type="primary")
        if search_btn and loc_search_input.strip():
            st.session_state.filter_home_loc = loc_search_input.strip()
            st.toast(f"Searching for {loc_search_input.strip()}")
        
        c1, c2, c3 = st.columns([3, 3, 3])
        with c1: h_loc = st.selectbox("📍 LOCATION", MUTARE_LOCATIONS, key="filter_home_loc")
        with c2: h_type = st.selectbox("🏠 ROOM TYPE", ROOM_TYPES, key="filter_home_type")
        with c3: h_price = st.selectbox("💷 MAX PRICE (USD)", ["Any budget", "$40", "$60", "$80", "$100", "$150+"], key="filter_home_price")
        # If search input provided, override location filter with fuzzy match
        if loc_search_input and loc_search_input.strip():
            # Try to match location containing search term
            search_term = loc_search_input.strip().lower()
            matched_locs = [loc for loc in MUTARE_LOCATIONS if search_term in loc.lower()]
            if matched_locs:
                h_loc = matched_locs[0]  # use first match
                st.info(f"🔍 Found location: {h_loc} for search '{loc_search_input}'")
            else:
                # Keep search as custom filter
                h_loc = loc_search_input.strip()
    st.divider()
    has_active_filter = (h_loc!= "All Locations") or (h_type!= "All Types") or (h_price!= "Any budget") or (loc_search_input and loc_search_input.strip()!="")
    if has_active_filter:
        filtered_rooms = st.session_state.db["rooms"]
        if h_loc!= "All Locations":
            # Support partial search
            if h_loc in MUTARE_LOCATIONS:
                filtered_rooms = [r for r in filtered_rooms if r.get("loc") == h_loc]
            else:
                # Custom search term - partial match
                filtered_rooms = [r for r in filtered_rooms if h_loc.lower() in r.get("loc","").lower()]
        if h_type!= "All Types": filtered_rooms = [r for r in filtered_rooms if r.get("type") == h_type]
        if h_price!= "Any budget":
            try:
                max_p = int(re.sub(r"\D", "", h_price))
                filtered_rooms = [r for r in filtered_rooms if float(r.get("price", 0)) <= max_p]
            except:
                pass
        filtered_rooms = [r for r in filtered_rooms if r.get("status") not in ["Rented", "Taken"]]
        filtered_rooms = sorted(filtered_rooms, key=lambda x: (not x.get("is_featured", False), x.get("created_at", "")), reverse=True)
        st.subheader(f"Matching Available Rooms ({len(filtered_rooms)} Found)")
        if not filtered_rooms: st.warning("🏠 No matching rooms found.")
        else:
            for idx, room in enumerate(filtered_rooms): render_property_card(room, idx, category_type="Room")
    else:
        st.subheader("⭐ Promoted & Featured Listings Browser")
        home_feat_tab1, home_feat_tab2, home_feat_tab3 = st.tabs(["⭐ Featured Rental Rooms","⭐ Featured Student Accommodation","⭐ Featured Houses For Sale"])
        with home_feat_tab1:
            feat_rooms = [r for r in st.session_state.db["rooms"] if r.get("is_featured", False) and r.get("status") not in ["Rented", "Taken"]]
            if not feat_rooms: st.info("🌟 No featured standard rooms active right now.")
            else:
                for idx, room in enumerate(feat_rooms): render_property_card(room, idx, category_type="Featured Room Home")
        with home_feat_tab2:
            feat_student = [s for s in st.session_state.db["student_rooms"] if s.get("is_featured", False) and s.get("status") not in ["Rented", "Taken"]]
            if not feat_student: st.info("🎓 No featured student accommodations.")
            else:
                for idx, s_room in enumerate(feat_student): render_property_card(s_room, idx, category_type="Featured Student Housing Home")
        with home_feat_tab3:
            feat_houses = [h for h in st.session_state.db["houses_sale"] if h.get("is_featured", False)]
            if not feat_houses: st.info("🏠 No featured properties for sale.")
            else:
                for idx, house in enumerate(feat_houses): render_property_card(house, idx, category_type="Featured Property Sale Home")
    st.divider(); render_middleman_banner()

elif selected_tab == "Browse Rooms":
    st.title("Browse Standard Rooms")
    st.markdown("""<div class="promo-banner">🚀 <b>Landlords! Boost Your Views:</b> Feature your room listing on top for <b>$2 for 7 Days</b> or <b>$5 for 30 Days</b> to get maximum tenant inquiries!</div>""", unsafe_allow_html=True)
    sub_tab1, sub_tab2 = st.tabs(["📋 All Rooms", "⭐ Featured Listings"])
    with sub_tab1:
        filter_loc = st.selectbox("📍 Filter by Suburb / Location:", MUTARE_LOCATIONS, key="browse_loc_filter")
        st.divider()
        rooms_list = [r for r in st.session_state.db["rooms"] if r.get("status") not in ["Rented", "Taken"]]
        if filter_loc!= "All Locations": rooms_list = [r for r in rooms_list if r.get("loc") == filter_loc]
        sorted_rooms = sorted(rooms_list, key=lambda x: (not x.get("is_featured", False), x.get("created_at", "")), reverse=True)
        if not sorted_rooms: st.info("🏠 No standard rooms posted under this location yet.")
        else:
            for idx, room in enumerate(sorted_rooms): render_property_card(room, idx, category_type="Room")
    with sub_tab2:
        featured_only = [r for r in st.session_state.db["rooms"] if r.get("is_featured", False) and r.get("status") not in ["Rented", "Taken"]]
        if not featured_only: st.info("🌟 No featured room listings active right now.")
        else:
            for idx, room in enumerate(featured_only): render_property_card(room, idx, category_type="Featured Room")

elif selected_tab == "Student Accommodation":
    st.title("🎓 Student Accommodation & Requests")
    st.markdown('''
    <div class="feature-ad-banner">
        <div class="ad-title">🎓 STUDENT ACCOMMODATION - HIGH DEMAND - FEATURE NOW!</div>
        <p class="ad-main">🏫 Target: Mutare Polytechnic, Africa University, MSUAS, Midlands State. Students search daily - be on top!</p>
        <div class="ad-prices">
            <span class="price-pill">⭐ $3 / 7 Days Featured - Top Student Tab</span>
            <span class="price-pill green">🚀 $6 / 30 Days Featured - 4x More Student Inquiries</span>
            <span class="price-pill blue">🎯 Free Posting - 21 Days Auto - Feature for Priority</span>
        </div>
        <p class="ad-footer">Students prefer: Near campus + WhatsApp contact + Clear house rules. Add all for faster letting!</p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("""<div class="promo-banner">🎓 <b>Students & Landlords:</b> Requests expire after <b>21 days</b> auto-delete! Promote housing for <b>$3 / 7 Days</b> or <b>$6 / 30 Days</b>!</div>""", unsafe_allow_html=True)
    st_tab1, st_tab2, st_tab3 = st.tabs(["📋 All Student Housing","🎓 Student Requests (21d)","⭐ Featured Student Rooms"])
    with st_tab1:
        if st.session_state.user_role == "Landlord" or is_owner():
            with st.expander("➕ Post Student Accommodation", expanded=False):
                with st.form("student_post_form"):
                    s_title = st.text_input("Property / Room Title *")
                    s_school = st.selectbox("🎓 Target College / University *", ["Mutare Polytechnic","Africa University","Midlands State University (Mutare)","Manicaland State University (MSUAS)","Other"])
                    s_loc = st.selectbox("📍 Location *", MUTARE_LOCATIONS[1:])
                    s_type = st.selectbox("🏠 Room Type *", ROOM_TYPES[1:])
                    s_price = st.text_input("Price Per Student / Month (USD) *")
                    s1, s2 = st.columns(2)
                    with s1: s_phone_wa = st.text_input("WhatsApp Number *", value=st.session_state.user_phone)
                    with s2: s_phone_call = st.text_input("Phone Number for Calls *", value=st.session_state.user_phone)
                    s_imgs = st.file_uploader("Upload Room Photos (Up to 7 Photos)", type=IMAGE_TYPES_ALLOWED, accept_multiple_files=True)
                    s_desc = st.text_area("Accommodation Description")
                    s_rules = st.text_area("House Rules / Do's & Don'ts *")
                    s_submit = st.form_submit_button("Post Student Room Now 🚀", use_container_width=True)
                    if s_submit:
                        encoded_imgs = [process_uploaded_image(img) for img in (s_imgs or []) if img is not None]
                        encoded_imgs = [img for img in encoded_imgs if img is not None]
                        is_dup = any(is_image_duplicate(st.session_state.db, img) for img in encoded_imgs)
                        if is_dup: st.error("🚫 Already listed!")
                        elif not s_title or not s_price or not validate_zw_phone(s_phone_wa) or not validate_zw_phone(s_phone_call): st.error("⚠️ Fill all fields")
                        else:
                            now_dt = datetime.now()
                            expiry_days_s = 3650 if is_owner() else 21
                            st.session_state.db["student_rooms"].insert(0, {"id": len(st.session_state.db["student_rooms"]) + 1,"title": s_title,"school": s_school,"loc": s_loc,"type": s_type,"price": s_price,"contact_wa": s_phone_wa,"contact_call": s_phone_call,"imgs": encoded_imgs[:7],"desc": s_desc,"rules": s_rules,"is_featured": False,"status": "Available","created_at": now_dt.isoformat(),"expires_at": (now_dt + timedelta(days=expiry_days_s)).isoformat(),"posted_by_name": st.session_state.user_name,"posted_by_phone": re.sub(r"\D", "", st.session_state.user_phone)})
                            if save_persistent_db(st.session_state.db):
                                st.session_state["just_posted"] = {"type": "Student Accommodation", "title": s_title, "expiry": expiry_days_s}
                                st.session_state.navigation = "Dashboard"
                                show_post_success_message("Student Accommodation", s_title, expiry_days_s, "Target: "+s_school)
                                st.rerun()
        st.divider()
        student_db = [s for s in st.session_state.db["student_rooms"] if s.get("status") not in ["Rented", "Taken"]]
        student_db = sorted(student_db, key=lambda x: (not x.get("is_featured", False), x.get("created_at", "")), reverse=True)
        if not student_db: st.info("🎓 No student accommodation listed yet.")
        else:
            for idx, s_room in enumerate(student_db): render_property_card(s_room, idx, category_type="Student Room")
    with st_tab2:
        st.subheader("🎓 Student Room Requests - 21 Days Auto-Delete")
        with st.expander("➕ Post Student Room Request", expanded=False):
            with st.form("student_request_form"):
                sr_name = st.text_input("Your Name *", value=st.session_state.user_name)
                sr_school = st.selectbox("🎓 Target College / University *", ["Mutare Polytechnic","Africa University","Midlands State University (Mutare)","Manicaland State University (MSUAS)","Other"])
                sr_loc = st.selectbox("📍 Preferred Location / Suburb *", MUTARE_LOCATIONS[1:])
                sr_budget = st.text_input("Max Budget Per Month ($ USD) *")
                sr_type = st.selectbox("🏠 Room Type Needed", ROOM_TYPES[1:])
                src1, src2 = st.columns(2)
                with src1: sr_phone_wa = st.text_input("WhatsApp Number *", value=st.session_state.user_phone)
                with src2: sr_phone_call = st.text_input("Direct Call Phone Number *", value=st.session_state.user_phone)
                sr_pref = st.text_area("Specific Student Requirements *")
                sr_submit = st.form_submit_button("Post Student Request 🚀", use_container_width=True)
                if sr_submit:
                    if sr_name and sr_budget and validate_zw_phone(sr_phone_wa) and validate_zw_phone(sr_phone_call):
                        st.session_state.db.setdefault("student_requests", []).insert(0, {"id": len(st.session_state.db["student_requests"]) + 1,"name": sr_name,"school": sr_school,"loc": sr_loc,"budget": sr_budget,"type": sr_type,"contact_wa": sr_phone_wa,"contact_call": sr_phone_call,"preferences": sr_pref,"created_at": datetime.now().isoformat(),"posted_by_name": st.session_state.user_name,"posted_by_phone": re.sub(r"\D", "", st.session_state.user_phone)})
                        if save_persistent_db(st.session_state.db):
                            st.session_state["just_posted"] = {"type": "Student Request", "title": sr_name, "expiry": 21}
                            st.session_state.navigation = "Dashboard"
                            show_post_success_message("Student Room Request", sr_name, 21, f"School: {sr_school} | Budget: ${sr_budget}")
                            st.rerun()
        st.divider()
        student_reqs_db = st.session_state.db.get("student_requests", [])
        if not student_reqs_db: st.info("🔍 No active student room requests.")
        else:
            for idx, sreq in enumerate(student_reqs_db):
                with st.container(border=True):
                    cd = format_countdown((datetime.fromisoformat(sreq['created_at']) + timedelta(days=21)).isoformat()) if sreq.get('created_at') else None
                    if cd: st.markdown(f'<div class="countdown-badge">{cd}</div>', unsafe_allow_html=True)
                    st.subheader(f"🎓 {sreq['name']} — {sreq['school']}")
                    st.write(f"📍 {sreq['loc']} | 🏠 {sreq['type']} | 💷 ${sreq['budget']}/mo")
                    st.info(f"📝 {sreq.get('preferences', 'None listed.')}")
                    st.write(f"💬 `{sreq['contact_wa']}` | 📞 `{sreq.get('contact_call', 'N/A')}`")
                    sb1, sb2 = st.columns(2)
                    with sb1: wa_url = format_wa_inquiry_link(sreq["contact_wa"], f"Student Room Request near {sreq['school']}", sreq["budget"], category="Student Request"); st.link_button("💬 WhatsApp Student", wa_url)
                    with sb2: st.link_button("📞 Call Student", f"tel:{sreq.get('contact_call', sreq['contact_wa'])}")
    with st_tab3:
        feat_student = [s for s in st.session_state.db["student_rooms"] if s.get("is_featured", False) and s.get("status") not in ["Rented", "Taken"]]
        if not feat_student: st.info("🌟 No featured student accommodations active currently.")
        else:
            for idx, s_room in enumerate(feat_student): render_property_card(s_room, idx, category_type="Featured Student Room")

elif selected_tab == "Houses for Sale":
    st.title("Houses & Property for Sale")
    st.markdown('''
    <div class="feature-ad-banner">
        <div class="ad-title">🏘️ HOUSES & STANDS FOR SALE - PREMIUM ADVERTISING!</div>
        <p class="ad-main">🏠 Sell faster with featured listings! Your property appears on Home page top & gets verified badge.</p>
        <div class="ad-prices">
            <span class="price-pill">🆓 2 FREE Listings - 21 Days Each</span>
            <span class="price-pill green">💰 $3 Extra Listing Fee</span>
            <span class="price-pill blue">⭐ $15 / 30 Days Featured - Top Home + Search</span>
            <span class="price-pill" style="background:#422006 !important; color:#FEF9C3 !important; border-color:#FACC15 !important;">👑 $20 VIP Unlimited 30 Days - Post Unlimited Houses!</span>
        </div>
        <p class="ad-footer">Includes: Professional presentation • WhatsApp direct • National ID verified for trust • Expires 21 days (10 YEARS for owner)</p>
    </div>
    ''', unsafe_allow_html=True)
    st.markdown("""<div class="promo-banner">🏠 <b>Sellers:</b> 2 FREE listings! Extra $3 each. Featured $15 / 30d or VIP Unlimited $20</div>""", unsafe_allow_html=True)
    hs_tab1, hs_tab2 = st.tabs(["🏠 All Houses & Stands", "⭐ Featured Sale Listings"])
    with hs_tab1:
        if st.session_state.user_role == "Landlord" or is_owner():
            user_phone_clean = canonical_phone(st.session_state.user_phone)
            current_user_obj = next((u for u in st.session_state.db.get("users", []) if u.get("phone") == user_phone_clean), {})
            user_posted_count = len([h for h in st.session_state.db.get("houses_sale", []) if h.get("posted_by_phone") == user_phone_clean])
            is_vip_active = current_user_obj.get("is_vip", False)
            if is_vip_active and current_user_obj.get("vip_until"):
                try:
                    if datetime.now() > datetime.fromisoformat(current_user_obj.get("vip_until")): is_vip_active=False
                except: pass
            paid_slots = current_user_obj.get("paid_house_slots", 0)
            can_post = False
            if is_owner() or is_vip_active:
                can_post = True; expander_label = "➕ Post a House or Stand for Sale"
            elif user_posted_count < 2:
                can_post = True; free_left = 2 - user_posted_count; expander_label = f"➕ Post a House or Stand for Sale ({free_left} FREE Remaining)"
            elif paid_slots > 0:
                can_post = True; expander_label = f"➕ Post a House or Stand for Sale ({paid_slots} Paid Slot)"
            else:
                can_post = False; expander_label = "➕ Post a House or Stand for Sale (⚠️ Limit Reached - $3 USD Fee Required)"
            with st.expander(expander_label, expanded=False):
                if not can_post:
                    st.error("⛔ Limit Reached! Pay $3 under Payments tab.")
                else:
                    with st.form("sale_post_form"):
                        h_title = st.text_input("Property Title *")
                        h_type = st.selectbox("🏘️ Property Type *", PROPERTY_TYPES_SALE)
                        h_loc = st.selectbox("📍 Location / Suburb *", MUTARE_LOCATIONS[1:])
                        h_address = st.text_input("Exact Property Physical Address *")
                        h_price = st.text_input("Selling Price ($ USD) *")
                        h1, h2 = st.columns(2)
                        with h1: h_phone_wa = st.text_input("Seller WhatsApp *", value=st.session_state.user_phone)
                        with h2: h_phone_call = st.text_input("Seller Phone Number for Calls *", value=st.session_state.user_phone)
                        h_imgs = st.file_uploader("Upload Property Photos (Up to 7) - Only House Pictures *", type=IMAGE_TYPES_ALLOWED, accept_multiple_files=True)
                        h_desc = st.text_area("Property Details / Features")
                        h_submit = st.form_submit_button("Post Property for Sale 🚀", use_container_width=True)
                        if h_submit:
                            encoded_imgs = [process_uploaded_image(img) for img in (h_imgs or []) if img is not None]
                            encoded_imgs = [img for img in encoded_imgs if img is not None]
                            is_dup = any(is_image_duplicate(st.session_state.db, img) for img in encoded_imgs)
                            if not h_address.strip(): st.error("⚠️ Enter exact physical address.")
                            elif is_dup: st.error("🚫 Already listed!")
                            elif not h_title or not h_price or not validate_zw_phone(h_phone_wa) or not validate_zw_phone(h_phone_call): st.error("⚠️ Fill all required fields")
                            else:
                                now_dt = datetime.now()
                                expiry_days_h = 3650 if is_owner() else 21
                                st.session_state.db["houses_sale"].insert(0, {"id": len(st.session_state.db["houses_sale"]) + 1,"title": h_title,"type": h_type,"loc": h_loc,"address": h_address,"price": h_price,"contact_wa": h_phone_wa,"contact_call": h_phone_call,"imgs": encoded_imgs[:7],"desc": h_desc,"is_featured": False,"created_at": now_dt.isoformat(),"expires_at": (now_dt + timedelta(days=expiry_days_h)).isoformat(),"posted_by_name": st.session_state.user_name,"posted_by_phone": user_phone_clean})
                                if not is_owner() and not is_vip_active and user_posted_count >= 2: current_user_obj["paid_house_slots"] = max(0, current_user_obj.get("paid_house_slots", 1) - 1)
                                if save_persistent_db(st.session_state.db):
                                    st.session_state["just_posted"] = {"type": "House Sale", "title": h_title, "expiry": expiry_days_h}
                                    st.session_state.navigation = "Dashboard"
                                    show_post_success_message("House/Stand for Sale", h_title, expiry_days_h, f"Location: {h_loc} | Price: ${h_price}")
                                    st.rerun()
        st.divider()
        houses_db = sorted(st.session_state.db["houses_sale"], key=lambda x: (not x.get("is_featured", False), x.get("created_at", "")), reverse=True)
        if not houses_db: st.info("🏠 No houses or stands currently listed for sale.")
        else:
            for idx, house in enumerate(houses_db): render_property_card(house, idx, category_type="Property Sale")
    with hs_tab2:
        feat_houses = [h for h in st.session_state.db["houses_sale"] if h.get("is_featured", False)]
        if not feat_houses: st.info("🌟 No featured properties for sale at the moment.")
        else:
            for idx, house in enumerate(feat_houses): render_property_card(house, idx, category_type="Featured Property Sale")

elif selected_tab == "Car Hire (Transport)":
    st.title("🚚 Mutare Goods & Moving Transport")
    # ===== NEW BANNER - CAR HIRE PROCEDURES =====
    st.markdown("""
    <div class="feature-ad-banner" style="border-left-color:#00FF88 !important;">
        <div class="ad-title">🚚 CAR HIRE - TRANSPORT FOR PEOPLE & PROPERTY MOVING</div>
        <p class="ad-main">🚀 <b>What is Car Hire Tab?</b> This is where verified drivers who transport people and help move properties, furniture, and goods are listed. Tenants & landlords can find affordable transport in Mutare.</p>
        <div class="ad-prices">
            <span class="price-pill" style="background:#0F172A !important; color:#FFFFFF !important;">📋 Step 1: Fill driver & vehicle details below</span>
            <span class="price-pill green">📸 Step 2: Upload Vehicle Photos (Up to 7 Required)</span>
            <span class="price-pill blue">💷 Step 3: Pay $5 EcoCash to 078 985 1813 & Submit Ref</span>
            <span class="price-pill" style="background:#FEF08A !important; color:#0F172A !important;">✅ Step 4: Admin verifies in <2 hrs - You go LIVE!</span>
        </div>
        <p class="ad-footer">⚠️ Vehicle photos are MANDATORY - Listings without vehicle pictures will not be approved. No driver photo needed. Transport people, move houses, deliver goods.</p>
    </div>
    """, unsafe_allow_html=True)
    with st.expander("🚚 Register Transport Listing ($5 USD / 30 Days)", expanded=False):
        with st.form("driver_post_form"):
            d_name = st.text_input("Driver / Business Name *")
            d_phone_wa = st.text_input("WhatsApp Number *", value=st.session_state.user_phone)
            d_phone_call = st.text_input("Direct Call Phone Number *", value=st.session_state.user_phone)
            d_area = st.selectbox("📍 Primary Operating Area *", MUTARE_LOCATIONS[1:])
            d_vtype = st.selectbox("🚚 Vehicle Type & Capacity *", VEHICLE_TYPES)
            d_rates = st.text_input("Base Rates / Pricing Info")
            d_desc = st.text_area("Services Offered & Details *")
            v_photos = st.file_uploader("Upload Vehicle Photos * (Required - Up to 7)", type=IMAGE_TYPES_ALLOWED, accept_multiple_files=True, key="vehicle_pics")
            st.caption("📸 Upload up to 7 clear vehicle photos - Front, Back, Inside, Loaded example - MANDATORY")
            st.markdown("---")
            st.markdown("""
            <div class="ecocash-payment-details" style="background: rgba(240,253,244,0.92) !important; backdrop-filter: blur(10px);">
                <div class="ecocash-payment-details-header">💷 EcoCash Payment Details ($5.00 USD / 30 Days)</div>
                <p style="margin:8px 0;"><b>Send $5 to EcoCash:</b></p>
                <p style="font-size:20px; font-weight:900; color:#16A34A !important; margin:4px 0;">078 985 1813 (Lewis G Kajayi)</p>
                <p style="font-size:14px; color:#334155 !important;">Then enter reference below - must be exact from SMS</p>
            </div>
            """, unsafe_allow_html=True)
            c_p1, c_p2 = st.columns(2)
            with c_p1: d_payer_name = st.text_input("Name of Person Who Performed Transaction *", value=st.session_state.user_name)
            with c_p2: d_payer_phone = st.text_input("Phone Number Used for EcoCash Payment *", value=st.session_state.user_phone)
            d_ecocash_ref = st.text_input("EcoCash Transaction Reference *", placeholder="e.g. PP230512.1241.A12345")
            d_submit = st.form_submit_button("Submit Driver Listing & Payment 🚀", use_container_width=True, type="primary")
            if d_submit:
                clean_ref = d_ecocash_ref.strip().upper() if d_ecocash_ref else ""
                stored_refs = st.session_state.db.get("verified_references", [])
                pending_refs = [p.get("reference") for p in st.session_state.db.get("pending_payments", [])]
                if is_owner() and not clean_ref:
                    clean_ref = "ADMIN-BYPASS-" + datetime.now().strftime("%Y%m%d%H%M%S")
                if not v_photos or len(v_photos) == 0: st.error("⚠️ Vehicle Photos Required - Upload at least 1 vehicle photo (up to 7)")
                elif len(v_photos) > 7: st.error("⚠️ Maximum 7 vehicle photos allowed")
                elif not d_name or not validate_zw_phone(d_phone_wa) or not validate_zw_phone(d_phone_call): st.error("⚠️ Fill valid contact")
                elif not validate_zw_phone(d_payer_phone): st.error("⚠️ Valid EcoCash phone required")
                elif not is_owner() and not validate_ecocash_ref(clean_ref): st.error("❌ Invalid Reference Code! Enter exact code from EcoCash SMS")
                elif not is_owner() and (clean_ref in stored_refs or clean_ref in pending_refs): st.error("⛔ DUPLICATE CODE - Already used!")
                else:
                    encoded_vehicle_imgs = [process_uploaded_image(img) for img in (v_photos or []) if img is not None]
                    encoded_vehicle_imgs = [img for img in encoded_vehicle_imgs if img is not None][:7]
                    if not encoded_vehicle_imgs: st.error("⚠️ Vehicle images failed to process - try JPG/PNG")
                    else:
                        now_dt = datetime.now(); expire_dt = now_dt + timedelta(days=30)
                        new_driver_id = len(st.session_state.db["car_hire"]) + 1
                        auto_approved = is_owner()
                        new_driver = {"id": new_driver_id,"name": d_name,"phone_wa": d_phone_wa,"phone_call": d_phone_call,"area": d_area,"vtype": d_vtype,"rates": d_rates,"desc": d_desc,"vehicle_imgs": encoded_vehicle_imgs,"vehicle_img": encoded_vehicle_imgs[0] if encoded_vehicle_imgs else None,"posted_by_name": st.session_state.user_name,"posted_by_phone": re.sub(r"\D", "", st.session_state.user_phone),"registered_at": now_dt.isoformat(),"expires_at": expire_dt.isoformat(),"is_approved": auto_approved}
                        st.session_state.db["car_hire"].insert(0, new_driver)
                    new_payment = {"id": len(st.session_state.db.get("pending_payments", [])) + len(st.session_state.db.get("approved_payments", [])) + 1,"account_name": st.session_state.user_name,"account_phone": re.sub(r"\D", "", st.session_state.user_phone),"payer_name": d_payer_name.strip(),"payer_phone": re.sub(r"\D", "", d_payer_phone),"package_name": "Car Hire / Transporter Listing (30 Days)","package_price": 5.0,"package_days": 30,"reference": clean_ref if clean_ref else "ADMIN-BYPASS","feature_target": {"db_key": "car_hire","id": new_driver_id,"days": 30,"title": d_name},"submitted_at": now_dt.isoformat(),"status": "Pending Verification","needs_correction": False}
                    if auto_approved:
                        new_payment["status"] = "Verified & Approved"; st.session_state.db["approved_payments"].append(new_payment); activate_payment_package(new_payment)
                        if save_persistent_db(st.session_state.db):
                            st.balloons()
                            st.session_state["just_posted"] = {"type": "Car Hire", "title": d_name, "expiry": 30}
                            st.session_state.navigation = "Dashboard"
                            show_post_success_message("Car Hire Listing", d_name, 30, "Status: APPROVED")
                            st.rerun()
                    else:
                        st.session_state.db["pending_payments"].append(new_payment)
                        if save_persistent_db(st.session_state.db):
                            st.balloons()
                            st.markdown(f"""<div class="success-post-banner" style="border-color: #F59E0B;"><h3 style="color: #92400E!important;">⏳ Application Received - Under Review!</h3><p>Your driver listing <b>{d_name}</b> and payment reference <b>{clean_ref}</b> have been received.</p><p>🔍 Admin verifying - LIVE in <2 hours!</p></div>""", unsafe_allow_html=True)
                            st.session_state["just_posted"] = {"type": "Car Hire - Pending Approval", "title": d_name, "expiry": 30}
                            st.session_state.navigation = "Dashboard"
                            import time; time.sleep(2); st.rerun()
    st.divider()
    active_drivers = [d for d in st.session_state.db.get("car_hire", []) if d.get("is_approved", False) or is_owner()]
    if not active_drivers: st.info("🚚 No active verified drivers")
    else:
        for idx, driver in enumerate(active_drivers):
            with st.container(border=True):
                if not driver.get("is_approved"): st.warning("🟡 PENDING ADMIN APPROVAL - Only Admin can see this")
                st.subheader(f"🚚 {driver['name']}")
                st.write(f"📍 {driver['area']} | 🚚 {driver['vtype']} | 💷 {driver.get('rates', 'Negotiable')}")
                st.write(f"📝 {driver.get('desc', 'N/A')}")
                st.write(f"💬 `{driver['phone_wa']}` | 📞 `{driver.get('phone_call', 'N/A')}`")
                # Vehicle gallery up to 7
                v_imgs = driver.get("vehicle_imgs") or ([driver.get("vehicle_img")] if driver.get("vehicle_img") else [])
                if v_imgs:
                    render_image_gallery(v_imgs, f"car_hire_gallery_{idx}", compact=True)
                # Contact buttons
                b1, b2 = st.columns(2)
                with b1:
                    wa_url = format_wa_inquiry_link(driver["phone_wa"], f"Car Hire {driver['name']} - {driver['vtype']}", driver.get("rates",""), category="Car Hire")
                    st.link_button("💬 WhatsApp Driver", wa_url, use_container_width=True)
                with b2:
                    st.link_button("📞 Call Driver", f"tel:{driver.get('phone_call', driver['phone_wa'])}", use_container_width=True)

elif selected_tab == "Post Room":
    if st.session_state.user_role!= "Landlord" and not is_owner(): st.error("⛔ Access Denied: Tenants are not permitted to post")
    else:
        st.title("Post a Room for Tenants")
        # BANNER - Post Room tab advertising
        st.markdown('''
        <div class="feature-ad-banner">
            <div class="ad-title">🚀 POST ROOM - FEATURE TO GET 5X MORE TENANTS!</div>
            <p class="ad-main">🏠 Free: 5 rooms per month (21 days each). Need more? Upgrade to Agent packages!</p>
            <div class="ad-prices">
                <span class="price-pill">💎 $2 / 7 Days - Featured Badge + Top</span>
                <span class="price-pill green">⭐ $5 / 30 Days - 5x Inquiries</span>
                <span class="price-pill blue">👑 Agent $10/30d - 25 listings • Agency/Business $20 - Unlimited listing</span>
                <span class="price-pill">🔥 Hot Deal Banner $4 / 7 Days</span>
            </div>
            <p class="ad-footer">After posting, go to Dashboard → Manage Package → Payments tab to feature your room. Admin approves in &lt;1 hour!</p>
        </div>
        ''', unsafe_allow_html=True)
        # Encouraging check requests banner
        st.markdown('''
        <div class="feature-ad-banner" style="border-left-color:#00FF88 !important;">
            <div class="ad-title">📩 MEET TENANT NEEDS - CHECK REQUESTS TAB!</div>
            <p class="ad-main">Tenants post daily what they are looking for. Browse <b>Requests (Wanted)</b> to tailor your listing & fill rooms faster!</p>
        </div>
        ''', unsafe_allow_html=True)
        user_phone_clean = canonical_phone(st.session_state.user_phone)
        current_u = next((u for u in st.session_state.db.get("users", []) if u.get("phone") == user_phone_clean), {})
        now_dt = datetime.now()
        last_reset_str = current_u.get("last_post_reset", now_dt.isoformat())
        try: last_reset_dt = datetime.fromisoformat(last_reset_str)
        except Exception: last_reset_dt = now_dt
        next_reset_dt = last_reset_dt + timedelta(days=30)
        if now_dt >= next_reset_dt:
            current_u["monthly_free_posts"] = 0; current_u["last_post_reset"] = now_dt.isoformat(); save_persistent_db(st.session_state.db)
            last_reset_dt = now_dt
            next_reset_dt = now_dt + timedelta(days=30)
        agent_pkg = current_u.get("agent_package")
        agent_until_str = current_u.get("agent_package_until")
        agent_expire_countdown = None
        if agent_pkg and agent_until_str:
            try:
                until_dt = datetime.fromisoformat(agent_until_str)
                agent_expire_countdown = format_countdown(agent_until_str)
                if datetime.now() > until_dt:
                    agent_pkg = None; current_u["agent_package"] = None; current_u["agent_package_until"] = None; current_u["agent_active_limit"] = 0; save_persistent_db(st.session_state.db)
                    agent_expire_countdown = "Expired"
                else:
                    agent_expire_countdown = format_countdown(agent_until_str)
            except: pass
        agent_limit = current_u.get("agent_active_limit", 0)
        my_active_rooms = [r for r in st.session_state.db.get("rooms", []) if r.get("posted_by_phone") == user_phone_clean]
        active_room_count = len(my_active_rooms)
        free_used = current_u.get("monthly_free_posts", 0)
        free_left = max(0, 5 - free_used)

        # ===== SLOT DISPLAY BANNER =====
        if is_owner():
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0F172A 0%,#1E40AF 100%); border:1.5px solid #3B82F6; border-radius:12px; padding:14px; margin-bottom:12px;">
                <p style="color:#FFFFFF !important; font-weight:900; margin:0;">👑 Owner - Unlimited Listings</p>
            </div>
            """, unsafe_allow_html=True)
        elif agent_pkg:
            limit_display = "♾️ Unlimited" if agent_limit >= 99999 else f"{agent_limit}"
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#422006 0%,#F59E0B 100%); border:2px solid #FACC15; border-radius:12px; padding:14px; margin-bottom:12px;">
                <p style="color:#FFFFFF !important; font-weight:900; margin:0; font-size:15px;">{agent_pkg} Active - {active_room_count}/{limit_display} Used</p>
                <p style="color:#FEF9C3 !important; font-weight:700; margin:4px 0 0 0; font-size:12px;">{agent_expire_countdown} - After expiry: back to 5 free slots, extra listings depleted</p>
                <p style="color:#FFFFFF !important; font-size:11px; margin:6px 0 0 0;">Valid 30 days, cycle forever. After 30 days, package expires and rooms beyond 5 are removed.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            reset_in_days = (next_reset_dt - now_dt).days
            st.markdown(f"""
            <div style="background:rgba(255,255,255,0.92); border:2px solid #3B82F6; border-left:5px solid #3B82F6; border-radius:12px; padding:14px; margin-bottom:12px;">
                <p style="color:#0F172A !important; font-weight:900; margin:0; font-size:15px;">📦 Free Slots: {free_used}/5 Used - {free_left} Remaining</p>
                <p style="color:#1E40AF !important; font-weight:700; margin:4px 0 0 0; font-size:12px;">⏰ Resets: {next_reset_dt.strftime('%d %B %Y')} (in {reset_in_days} days) - Cycle repeats forever</p>
                <p style="color:#475569 !important; font-size:11px; margin:6px 0 0 0;">Each free listing expires after 21 days. After 30 days, you get 5 new free slots again. Upgrade to Agent $10/25 listings or $25 Unlimited (30 days) for more.</p>
            </div>
            """, unsafe_allow_html=True)
            # Show active rooms with countdown in dashboard style
            if my_active_rooms:
                st.caption(f"Your active rooms: {active_room_count} - they show countdown in Dashboard")

        can_post_room = False; duration_days = 21
        if is_owner(): can_post_room = True; duration_days = 30
        elif agent_pkg:
            if active_room_count < agent_limit:
                can_post_room = True; duration_days = 30
            else:
                can_post_room = False
                if agent_limit >= 99999:
                    st.error(f"⚠️ Unexpected limit - contact admin")
                else:
                    st.error(f"⛔ Agent Limit Reached {active_room_count}/{agent_limit} - Package: {agent_pkg} | Expires: {agent_expire_countdown}")
        else:
            if free_used < 5:
                can_post_room = True; duration_days = 21
            else:
                can_post_room = False
                st.error(f"⛔ 5 Free Slots Depleted - Resets on {next_reset_dt.strftime('%d %B %Y')} ({(next_reset_dt - now_dt).days} days left). After reset, you get 5 free again forever.")
                st.info("💡 Need more now? Buy Agent $10 (25 listings / 30 days) or Agency $25 (Unlimited / 30 days) in Payments tab.")
        if can_post_room:
            with st.container(border=True):
                with st.form("post_room_form"):
                    st.subheader("📝 Fill Room Details")
                    r_title = st.text_input("Room Title *")
                    r_loc = st.selectbox("📍 Suburbs / Location *", MUTARE_LOCATIONS[1:])
                    r_type = st.selectbox("🏠 Room Type *", ROOM_TYPES[1:])
                    r_price = st.text_input("Monthly Rent ($ USD) *")
                    c1, c2 = st.columns(2)
                    with c1: r_phone_wa = st.text_input("WhatsApp Contact Number *", value=st.session_state.user_phone)
                    with c2: r_phone_call = st.text_input("Phone Number for Direct Calls *", value=st.session_state.user_phone)
                    r_imgs = st.file_uploader("Upload Room Photos (Up to 7)", type=IMAGE_TYPES_ALLOWED, accept_multiple_files=True)
                    r_desc = st.text_area("Room Description")
                    r_rules = st.text_area("House Rules / Do's & Don'ts *")
                    post_btn = st.form_submit_button("Submit Room Listing 🚀", use_container_width=True, type="primary")
                    if post_btn:
                        encoded_imgs = [process_uploaded_image(img) for img in (r_imgs or []) if img is not None]
                        encoded_imgs = [img for img in encoded_imgs if img is not None]
                        is_dup = any(is_image_duplicate(st.session_state.db, img) for img in encoded_imgs)
                        if is_dup: st.error("🚫 Already listed!")
                        elif not r_title or not r_price or not validate_zw_phone(r_phone_wa) or not validate_zw_phone(r_phone_call): st.error("⚠️ Fill all fields")
                        else:
                            exp_time = (now_dt + timedelta(days=duration_days)).isoformat()
                            st.session_state.db["rooms"].insert(0, {"id": len(st.session_state.db["rooms"]) + 1,"title": r_title,"loc": r_loc,"type": r_type,"price": r_price,"contact_wa": r_phone_wa,"contact_call": r_phone_call,"imgs": encoded_imgs[:7],"desc": r_desc,"rules": r_rules,"status": "Available","is_featured": False,"created_at": now_dt.isoformat(),"expires_at": exp_time,"posted_by_name": st.session_state.user_name,"posted_by_phone": user_phone_clean})
                            if not agent_pkg and not is_owner(): current_u["monthly_free_posts"] = current_u.get("monthly_free_posts", 0) + 1
                            if save_persistent_db(st.session_state.db):
                                st.session_state["just_posted"] = {"type": "Room", "title": r_title, "expiry": duration_days}
                                st.session_state.navigation = "Dashboard"
                                show_post_success_message("Room for Rent", r_title, duration_days, f"Location: {r_loc} | Price: ${r_price}/mo")
                                st.rerun()

elif selected_tab == "Requests (Wanted)":
    st.title("Tenant Room Requests (Wanted) - 21 Days")
    st.caption("Auto-delete after 21 days")
    with st.expander("➕ Tenant: Post What Room You Are Looking For", expanded=False):
        with st.form("request_form"):
            st.subheader("📝 Tell Landlords What You Need")
            req_name = st.text_input("Your Name *", value=st.session_state.user_name)
            req_loc = st.selectbox("📍 Preferred Location *", MUTARE_LOCATIONS[1:])
            req_budget = st.text_input("Max Budget ($ USD) *")
            req_type = st.selectbox("🏠 Room Type Needed", ROOM_TYPES[1:])
            rc1, rc2 = st.columns(2)
            with rc1: req_phone_wa = st.text_input("WhatsApp Number *", value=st.session_state.user_phone)
            with rc2: req_phone_call = st.text_input("Direct Call Phone Number *", value=st.session_state.user_phone)
            req_pref = st.text_area("Preferences & Specific Needs *")
            req_submit = st.form_submit_button("Post Request 🚀", use_container_width=True, type="primary")
            if req_submit:
                if req_name and req_budget and validate_zw_phone(req_phone_wa) and validate_zw_phone(req_phone_call):
                    st.session_state.db["requests"].insert(0, {"id": len(st.session_state.db["requests"]) + 1,"name": req_name,"loc": req_loc,"budget": req_budget,"type": req_type,"contact_wa": req_phone_wa,"contact_call": req_phone_call,"preferences": req_pref,"created_at": datetime.now().isoformat(),"posted_by_name": st.session_state.user_name,"posted_by_phone": re.sub(r"\D", "", st.session_state.user_phone)})
                    if save_persistent_db(st.session_state.db):
                        st.session_state["just_posted"] = {"type": "Tenant Request", "title": req_name, "expiry": 21}
                        st.session_state.navigation = "Dashboard"
                        show_post_success_message("Tenant Room Request (Wanted)", req_name, 21, f"Location: {req_loc} | Budget: ${req_budget}")
                        st.rerun()
                else:
                    st.error("⚠️ Fill all required fields with valid phone numbers")
    st.divider()
    requests_db = st.session_state.db.get("requests", [])
    if not requests_db: st.info("🔍 No active tenant requests.")
    else:
        for idx, req in enumerate(requests_db):
            with st.container(border=True):
                cd = format_countdown((datetime.fromisoformat(req['created_at']) + timedelta(days=21)).isoformat()) if req.get('created_at') else None
                if cd: st.markdown(f'<div class="countdown-badge">{cd}</div>', unsafe_allow_html=True)
                st.subheader(f"👥 {req['name']}")
                st.write(f"📍 {req['loc']} | 🏠 {req['type']} | 💷 ${req['budget']}/mo")
                st.info(f"📝 {req.get('preferences', 'None')}")
                st.write(f"💬 `{req['contact_wa']}` | 📞 `{req.get('contact_call', 'N/A')}`")
                b1, b2 = st.columns(2)
                with b1: wa_url = format_wa_inquiry_link(req["contact_wa"], f"Room Request in {req['loc']}", req["budget"], category="Tenant Request"); st.link_button("💬 WhatsApp Tenant", wa_url)
                with b2: st.link_button("📞 Call Tenant", f"tel:{req.get('contact_call', req['contact_wa'])}")
    st.divider(); render_middleman_banner()

elif selected_tab == "Payments":
    st.title("💷 Purchase Top-Up & Feature Listings")
    st.markdown("""<div class="ecocash-banner"><h3>📱 OFFICIAL ECOCASH PAYMENT DETAILS</h3><p class="eco-name">NAME: Lewis G Kajayi</p><p class="eco-number">NUMBER: 078 985 1813</p><p>Send EXACT amount then submit reference below.<br>Use your EcoCash to send to above number.</p></div>""", unsafe_allow_html=True)
    room_packages = [
        {"name": "Featured Room (7 Days)","price": 2.0,"label": "⭐ Featured Standard Room (7 Days) ($2.00)","target_key": "rooms","requires_room": True,"days": 7},
        {"name": "Featured Room (30 Days)","price": 5.0,"label": "⭐ Featured Standard Room (30 Days) ($5.00)","target_key": "rooms","requires_room": True,"days": 30},
        {"name": "Rooms to Rent Agent ($10.00 / Month - 25 Active Listings)","price": 10.0,"label": "👑 Rooms to Rent Agent ($10.00 / Month) - Up to 25 Active Listings (30 Days)","target_key": None,"requires_room": False,"days": 30},
        {"name": "Rooms to Rent Agency/Business ($25.00 / Month - Unlimited)","price": 25.0,"label": "🏢 Rooms to Rent Agency/Business ($25.00 / Month) - Unlimited Listings (30 Days)","target_key": None,"requires_room": False,"days": 30},
        {"name": "HOT DEAL TOP SLOT (7 Days on 1 of 3 Big Cards)","price": 4.0,"label": "🔥 HOT DEAL TOP SLOT - Feature on 1 of 3 Big Home Cards (7 Days) ($4.00)","target_key": "rooms","requires_room": True,"days": 7,"is_hot_deal": True},
        {"name": "Student Accommodation Featured Room (7 Days)","price": 3.0,"label": "⭐ Student Accommodation Featured Room (7 Days) ($3.00)","target_key": "student_rooms","requires_room": True,"days": 7},
        {"name": "Student Accommodation Featured Room (30 Days)","price": 6.0,"label": "⭐ Student Accommodation Featured Room (30 Days) ($6.00)","target_key": "student_rooms","requires_room": True,"days": 30},
        {"name": "House / Stand Basic Listing Fee","price": 3.0,"label": "🏠 Basic House / Stand Listing Fee (1 Extra Slot) ($3.00)","target_key": None,"requires_room": False,"days": 0},
        {"name": "Featured House / Stand for Sale (30 Days)","price": 15.0,"label": "⭐ Featured House / Stand for Sale (30 Days) ($15.00)","target_key": "houses_sale","requires_room": True,"days": 30},
        {"name": "Agent / House For Sale VIP (30 Days Unlimited Listing)","price": 20.0,"label": "👑 Agent / House For Sale VIP - 30 Days Unlimited Listing ($20.00)","target_key": None,"requires_room": False,"days": 30},
        {"name": "Car Hire / Transporter Listing (30 Days)","price": 5.0,"label": "Car Hire / Transporter Listing (30 Days) ($5.00)","target_key": "car_hire","requires_room": True,"days": 30},
    ]
    dropdown_labels = [pkg["label"] for pkg in room_packages]
    with st.container(border=True):
        st.markdown("##### **1. SELECT PAYMENT PACKAGE**")
        chosen_label = st.selectbox("💸 Select Package", dropdown_labels, label_visibility="collapsed")
        target_idx = dropdown_labels.index(chosen_label); target_pkg = room_packages[target_idx]
        feature_target = None; hot_deal_slot_index = 0
        if target_pkg.get("is_hot_deal"):
            st.markdown("##### **SELECT HOT DEAL CARD SLOT**")
            hot_deals = st.session_state.db.get("hot_deals", [None, None, None])
            slot_options = []
            for s_i in range(3):
                status = "🔴 Occupied" if hot_deals[s_i] else "🟢 Free"
                slot_options.append(f"Big Card Slot #{s_i + 1} - [{status}]")
            chosen_slot_label = st.selectbox("🔥 Select Hot Deal Card Slot", slot_options)
            hot_deal_slot_index = slot_options.index(chosen_slot_label)
        if target_pkg["requires_room"]:
            st.markdown("##### **2. WHICH LISTING TO UNLOCK / FEATURE?**")
            user_phone_clean = canonical_phone(st.session_state.user_phone)
            db_key_needed = target_pkg["target_key"]
            target_db = st.session_state.db.get(db_key_needed, [])
            filtered_my_listings = [(db_key_needed, r) for r in target_db if r.get("posted_by_phone") == user_phone_clean]
            if not filtered_my_listings: st.warning("⚠️ You haven't registered any items under this category yet.")
            else:
                options_dict = {"-- Select an item --": None}
                for db_key, item in filtered_my_listings:
                    badge = "⭐ (Featured)" if item.get("is_featured") or item.get("is_approved") else ""
                    item_title = item.get("title", item.get("name", "Item")); item_price = item.get("price", item.get("rates", "N/A")); item_loc = item.get("loc", item.get("area", "N/A"))
                    label = f"{item_title} (${item_price}) - {item_loc} {badge}"
                    options_dict[label] = (db_key, item)
                selected_item_label = st.selectbox("🏠 Select item to feature", list(options_dict.keys()), label_visibility="collapsed")
                if selected_item_label!= "-- Select an item --":
                    chosen_db_key, chosen_item = options_dict[selected_item_label]
                    feature_target = {"db_key": chosen_db_key,"id": chosen_item["id"],"days": target_pkg["days"],"title": chosen_item.get("title", chosen_item.get("name"))}
        st.divider()
        st.markdown("##### **3. PAYMENT VERIFICATION DETAILS**")
        p1, p2 = st.columns(2)
        with p1: payer_name = st.text_input("Name of Person Who Performed Transaction *", value=st.session_state.user_name)
        with p2: payer_phone = st.text_input("Phone Number Used for EcoCash Payment *", value=st.session_state.user_phone)
        ecocash_ref = st.text_input("EcoCash Transaction Reference *", placeholder="e.g. PP230510.1241.A12345")
        if st.button("Verify Payment to Unlock Your Package 🚀", use_container_width=True, type="primary"):
            clean_ref = ecocash_ref.strip().upper() if ecocash_ref else ""
            stored_refs = st.session_state.db.get("verified_references", [])
            pending_refs = [p.get("reference") for p in st.session_state.db.get("pending_payments", [])]
            if is_owner() and not clean_ref:
                clean_ref = "ADMIN-BYPASS-" + datetime.now().strftime("%Y%m%d%H%M%S")
            if target_pkg["requires_room"] and not feature_target and not is_owner(): st.error("⚠️ Please select a listing")
            elif not payer_name.strip(): st.error("⚠️ Enter payer name")
            elif not validate_zw_phone(payer_phone): st.error("⚠️ Invalid EcoCash phone")
            elif not is_owner() and not validate_ecocash_ref(clean_ref): st.error("❌ Invalid Reference Code! Put exact code from EcoCash SMS.")
            elif not is_owner() and (clean_ref in stored_refs or clean_ref in pending_refs): st.error("⛔ DUPLICATE CODE - This reference was already used!")
            else:
                new_payment = {"id": len(st.session_state.db.get("pending_payments", [])) + len(st.session_state.db.get("approved_payments", [])) + 1001,"account_name": st.session_state.user_name,"account_phone": re.sub(r"\D", "", st.session_state.user_phone),"payer_name": payer_name.strip(),"payer_phone": re.sub(r"\D", "", payer_phone),"package_name": target_pkg["name"],"package_price": target_pkg["price"],"package_days": target_pkg["days"],"reference": clean_ref,"feature_target": feature_target,"hot_deal_slot_index": hot_deal_slot_index,"submitted_at": datetime.now().isoformat(),"status": "Pending Verification","needs_correction": False}
                if is_owner():
                    new_payment["status"] = "Verified & Approved"; new_payment["approved_at"] = datetime.now().isoformat()
                    st.session_state.db["approved_payments"].append(new_payment); st.session_state.db["verified_references"].append(clean_ref)
                    activate_payment_package(new_payment); save_persistent_db(st.session_state.db)
                    st.success("✅ Package activated successfully!"); st.balloons()
                else:
                    st.session_state.db["pending_payments"].append(new_payment)
                    save_persistent_db(st.session_state.db)
                    st.success("🌟 Payment Submitted! Admin will verify in <2 hours. Check Dashboard for status!"); st.balloons()

elif selected_tab == "Dashboard":
    # ===== MESSAGE APP STYLE NOTIFICATION SYSTEM =====
    user_phone_clean = canonical_phone(st.session_state.user_phone)
    # Calculate notifications that need attention
    my_pending_pays = [p for p in st.session_state.db.get("pending_payments", []) if p.get("account_phone") == user_phone_clean]
    my_approved_pays = [p for p in st.session_state.db.get("approved_payments", []) if p.get("account_phone") == user_phone_clean]
    needs_correction = [p for p in my_pending_pays if p.get("needs_correction")]
    unread_count = len([p for p in my_pending_pays if p.get("id") not in st.session_state.get("seen_payment_ids", set())]) + len(needs_correction)
    # Expiring soon
    my_rooms = [r for r in st.session_state.db.get("rooms", []) if r.get("posted_by_phone") == user_phone_clean]
    expiring_soon = []
    for r in my_rooms:
        cd = format_countdown(r.get("expires_at"))
        if cd and ("Expired" in cd or "h" in cd and "d" not in cd):  # expires within hours
            expiring_soon.append(r)
    
    total_notifications = unread_count + len(needs_correction) + len(expiring_soon)
    
    if total_notifications > 0:
        # POP UP NOTIFICATION - like message app
        st.markdown(f"""
        <div style="position:fixed; top:70px; right:20px; z-index:9999; background:linear-gradient(135deg,#EF4444 0%,#DC2626 100%); color:white; padding:12px 18px; border-radius:12px; box-shadow:0 8px 24px rgba(239,68,68,0.45); border:2px solid #FECACA; animation: pulse 2s infinite; max-width:320px;">
            <p style="margin:0; font-weight:900; font-size:14px;">🔔 {total_notifications} Notification{'s' if total_notifications>1 else ''} Need Attention!</p>
            <p style="margin:4px 0 0 0; font-size:11px; font-weight:600;">{"❌ Wrong EcoCash ref! " if needs_correction else ""}{"⏰ Listings expiring soon! " if expiring_soon else ""}{"📩 New package updates!" if unread_count>0 else ""}</p>
        </div>
        <style>@keyframes pulse {{0%{{transform:scale(1);}}50%{{transform:scale(1.03);}}100%{{transform:scale(1);}}}}</style>
        """, unsafe_allow_html=True)
        st.toast(f"🔔 You have {total_notifications} notifications that need attention!", icon="🔔")
        # Also show in top bar
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.12); border:1.5px solid #FCA5A5; border-left:5px solid #EF4444; border-radius:10px; padding:12px; margin-bottom:12px;">
            <p style="color:#991B1B !important; font-weight:900; margin:0; font-size:13px;">🔔 Message Center: {total_notifications} issue{'s' if total_notifications>1 else ''} need action</p>
            <p style="color:#7F1D1D !important; font-size:11px; margin:4px 0 0 0;">{ '❌ Fix EcoCash ref - tap below | ' if needs_correction else ''}{ '⏰ Renew expiring rooms | ' if expiring_soon else ''}Check your messages below</p>
        </div>
        """, unsafe_allow_html=True)

    # LANDLORD ENCOURAGEMENT - DELETE RENTED & FEATURE ROOMS
    if st.session_state.user_role == "Landlord" or is_owner():
        st.markdown('''
        <div style="background:rgba(255,255,255,0.18); backdrop-filter:blur(18px); border:1.5px solid rgba(255,255,255,0.35); border-left:5px solid #FACC15; border-radius:12px; padding:14px; margin:12px 0;">
        <p style="color:#FEF08A !important; font-weight:900; font-size:14px; margin:0;">💡 Landlord Tip - Keep Listings Fresh!</p>
        <p style="color:#FFFFFF !important; font-weight:600; font-size:12px; margin:6px 0 0 0;">✅ Delete rooms marked as <b>Rented/Taken</b> to keep your profile clean</p>
        <p style="color:#FFFFFF !important; font-weight:600; font-size:12px; margin:4px 0 0 0;">⭐ Feature your rooms for <b>$2/7days or $5/30days</b> to get 5x more inquiries!</p>
        <p style="color:#DBEAFE !important; font-size:11px; margin:6px 0 0 0;">Go to My Listings below → Use Feature & Delete buttons</p>
        </div>
        ''', unsafe_allow_html=True)
    st.divider()

    user_phone_clean = canonical_phone(st.session_state.user_phone)
    st.title("User Dashboard - Private to You")
    st.caption(f"🔒 Privacy: Only you {user_phone_clean} can see your data here")
    st.write(f"Logged in as: **{st.session_state.user_name}** (`{st.session_state.user_phone}`) | **{st.session_state.user_role}**")
    current_u = next((u for u in st.session_state.db.get("users", []) if u.get("phone") == user_phone_clean), {})
    if st.session_state.get("just_posted"):
        jp = st.session_state.get("just_posted")
        st.markdown(f"""<div class="success-post-banner"><h3>✅ SUCCESS! {jp.get("title")} is LIVE!</h3><p>Your <b>{jp.get("type")}</b> was posted successfully and is now visible to tenants on the platform!</p><p>📍 Manage it below in your private dashboard</p><p>⏰ Expiry: {jp.get("expiry")} days</p></div>""", unsafe_allow_html=True)
        st.balloons()
        if st.button("Clear Message & Continue", key="clear_just_posted"):
            del st.session_state["just_posted"]; st.rerun()
    my_pending_pays = [p for p in st.session_state.db.get("pending_payments", []) if p.get("account_phone") == user_phone_clean]
    my_approved_pays = [p for p in st.session_state.db.get("approved_payments", []) if p.get("account_phone") == user_phone_clean]
    if current_u.get("agent_package") and current_u.get("agent_package_until"):
        try:
            if datetime.now() > datetime.fromisoformat(current_u.get("agent_package_until")): st.warning(f"⚠️ Your {current_u.get('agent_package')} expired")
            else:
                limit_disp = "Unlimited" if current_u.get("agent_active_limit",0)>=99999 else str(current_u.get("agent_active_limit"))
                st.success(f"👑 **{current_u.get('agent_package')} Active** Limit: {limit_disp}")
        except: pass
    if current_u.get("is_vip"): st.success(f"👑 **VIP House/Stand Unlimited Active**")
    if current_u.get("paid_house_slots", 0) > 0: st.info(f"🏠 **Paid Slots:** {current_u.get('paid_house_slots')}")
    # --- Initialize cleared verified notifications ---
    if "cleared_verified_ids" not in st.session_state:
        st.session_state.cleared_verified_ids = set()

    if my_pending_pays or my_approved_pays:
        st.subheader("🔔 Verification & Package Status - Messages")
        st.caption(f"💬 Like WhatsApp - new messages show as unread, after you open Dashboard they mark as read")
        
        # Clear button row - only show if there are verified notifications
        visible_approved = [p for p in my_approved_pays if p.get("id") not in st.session_state.cleared_verified_ids]
        if visible_approved:
            c_title, c_btn = st.columns([3, 1])
            with c_btn:
                if st.button("🧹 Clear Notifications", key="clear_verified_notifs", help="Clear all verified notifications", use_container_width=True):
                    for ap in visible_approved:
                        st.session_state.cleared_verified_ids.add(ap.get("id"))
                    st.toast("✅ Verified notifications cleared!", icon="🧹")
                    st.rerun()
        
        for p_pay in my_pending_pays:
            ft = p_pay.get("feature_target") or {}
            item_name = ft.get("title") if isinstance(ft, dict) and ft.get("title") else p_pay.get("package_name")
            is_unread = p_pay.get("id") not in st.session_state.seen_payment_ids
            unread_dot = "🔵 NEW" if is_unread else "✅ Read"
            if p_pay.get("needs_correction"):
                st.markdown(f'<div class="verified-notif-card status-box-error-new">❌ <b>WRONG REF! {unread_dot}</b><br><code>{p_pay.get("reference")}</code> for <b>{item_name}</b><br><span style="font-size:12px; opacity:0.9;">{p_pay.get("correction_message","")}</span></div>', unsafe_allow_html=True)
                with st.container(border=True):
                    st.write(f"Correct reference for: **{item_name}**")
                    new_ref = st.text_input(f"Enter correct EcoCash code", key=f"correct_ref_{p_pay.get('id')}", placeholder="PP230510.1241.A12345")
                    if st.button(f"Resubmit Correct Code 🚀", key=f"resubmit_{p_pay.get('id')}", use_container_width=True):
                        clean_new = new_ref.strip().upper()
                        if not validate_ecocash_ref(clean_new): st.error("❌ Invalid format")
                        else:
                            stored_refs = st.session_state.db.get("verified_references", [])
                            pending_refs = [p.get("reference") for p in st.session_state.db.get("pending_payments", []) if p.get("id")!= p_pay.get("id")]
                            if clean_new in stored_refs or clean_new in pending_refs: st.error("⛔ Duplicate")
                            else:
                                p_pay["reference"] = clean_new; p_pay["needs_correction"] = False; p_pay.pop("correction_message", None)
                                save_persistent_db(st.session_state.db); st.success("✅ Corrected!"); st.rerun()
            else:
                st.markdown(f'<div class="verified-notif-card status-box-pending-new">⏳ <b>Pending Verification {unread_dot}:</b><br><code>{p_pay.get("reference")}</code> for <b>{item_name}</b><br><span style="font-size:12px;">Admin will approve in <2 hours</span></div>', unsafe_allow_html=True)
        for a_pay in my_approved_pays:
            if a_pay.get("id") in st.session_state.cleared_verified_ids:
                continue
            ft = a_pay.get("feature_target") or {}
            item_name = ft.get("title") if isinstance(ft, dict) and ft.get("title") else a_pay.get("package_name")
            app_at = a_pay.get("approved_at") or a_pay.get("submitted_at")
            is_unread = a_pay.get("id") not in st.session_state.seen_payment_ids
            unread_dot = "🔵 NEW - Just Approved!" if is_unread else "✅ Seen"
            try:
                exp_dt = datetime.fromisoformat(app_at) + timedelta(days=a_pay.get("package_days",30))
                countdown = format_countdown(exp_dt.isoformat())
            except: countdown = "Active"
            st.markdown(f'<div class="verified-notif-card status-box-approved-new">✅ <b>Verified & Active! {unread_dot}</b><br><code>{a_pay.get("reference")}</code> for <b>{item_name}</b><br><span style="font-size:12px; color:#86EFAC !important;">{countdown}</span></div>', unsafe_allow_html=True)
        st.divider()
    def render_landlord_manage_section_fixed(db_key, category_label):
        items_list = st.session_state.db.get(db_key, [])
        my_items = [(idx, item) for idx, item in enumerate(items_list) if item.get("posted_by_phone") == user_phone_clean]
        if not my_items:
            st.info(f"🔒 Private: No listings under {category_label} for your account {user_phone_clean}"); return
        st.caption(f"🔒 Private - Only your number {user_phone_clean} listings")
        for real_idx, item in my_items:
            render_property_card(item, real_idx, category_type=category_label, is_admin_view=True, show_countdown=True)
            b1, b2, b3 = st.columns(3)
            with b1:
                is_taken = item.get("status") in ["Rented", "Taken"]
                if not is_taken:
                    if st.button("🔴 Mark Room as Taken", key=f"taken_btn_{db_key}_{real_idx}"):
                        item["status"] = "Taken"; save_persistent_db(st.session_state.db); st.toast("Marked as taken!"); st.rerun()
                else:
                    if st.button("🟢 Mark as Available", key=f"avail_btn_{db_key}_{real_idx}"):
                        item["status"] = "Available"; save_persistent_db(st.session_state.db); st.toast("Available again!"); st.rerun()
            with b2:
                if st.button("✏️ Edit Details", key=f"edit_btn_{db_key}_{real_idx}"):
                    st.session_state.editing_item_type = db_key; st.session_state.editing_item_id = real_idx
            with b3:
                if st.button("Delete 🗑️", key=f"del_btn_{db_key}_{real_idx}", type="primary"):
                    st.session_state.db[db_key].pop(real_idx); save_persistent_db(st.session_state.db); st.rerun()
            if st.session_state.editing_item_type == db_key and st.session_state.editing_item_id == real_idx:
                st.markdown("---")
                st.subheader(f"✏️ Editing: {item.get('title', item.get('name'))}")
                with st.form(key=f"edit_form_{db_key}_{real_idx}"):
                    if db_key in ["rooms", "student_rooms", "houses_sale"]:
                        e_title = st.text_input("Title", value=item.get("title", "")); e_loc = st.selectbox("Location", MUTARE_LOCATIONS[1:], index=(MUTARE_LOCATIONS[1:].index(item["loc"]) if item.get("loc") in MUTARE_LOCATIONS[1:] else 0))
                        e_price = st.text_input("Price ($ USD)", value=str(item.get("price", "")))
                        e_phone_wa = st.text_input("WhatsApp Number", value=item.get("contact_wa", "")); e_phone_call = st.text_input("Call Phone Number", value=item.get("contact_call", ""))
                        e_desc = st.text_area("Description", value=item.get("desc", "")); save_edit = st.form_submit_button("Save Changes 💾", use_container_width=True)
                        if save_edit:
                            item["title"] = e_title.strip(); item["loc"] = e_loc; item["price"] = e_price.strip(); item["contact_wa"] = e_phone_wa.strip(); item["contact_call"] = e_phone_call.strip(); item["desc"] = e_desc.strip()
                            save_persistent_db(st.session_state.db); st.session_state.editing_item_type = None; st.session_state.editing_item_id = None; st.toast("Saved!"); st.rerun()
                    elif db_key == "car_hire":
                        e_name = st.text_input("Driver Name", value=item.get("name", "")); e_area = st.selectbox("Area", MUTARE_LOCATIONS[1:], index=(MUTARE_LOCATIONS[1:].index(item["area"]) if item.get("area") in MUTARE_LOCATIONS[1:] else 0))
                        e_rates = st.text_input("Rates", value=item.get("rates", "")); e_phone_wa = st.text_input("WhatsApp", value=item.get("phone_wa", "")); e_phone_call = st.text_input("Call", value=item.get("phone_call", "")); e_desc = st.text_area("Services", value=item.get("desc", "")); save_edit = st.form_submit_button("Save Changes 💾", use_container_width=True)
                        if save_edit:
                            item["name"] = e_name.strip(); item["area"] = e_area; item["rates"] = e_rates.strip(); item["phone_wa"] = e_phone_wa.strip(); item["phone_call"] = e_phone_call.strip(); item["desc"] = e_desc.strip()
                            save_persistent_db(st.session_state.db); st.session_state.editing_item_type = None; st.session_state.editing_item_id = None; st.toast("Saved!"); st.rerun()
    if st.session_state.user_role == "Tenant" and not is_owner():
        # ===== SIMPLIFIED TENANT DASHBOARD =====
        st.markdown("""
        <div class="feature-ad-banner" style="border-left-color:#00D9FF !important;">
            <div class="ad-title">👋 Welcome Tenant - Browse & Request Made Simple</div>
            <p class="ad-main">You are here to <b>browse rooms</b> and <b>post requests</b>. You can also register as a driver in Car Hire!</p>
        </div>
        """, unsafe_allow_html=True)
        t_c1, t_c2, t_c3 = st.columns(3)
        with t_c1:
            st.link_button("🏠 Browse Rooms", "#", use_container_width=True)
            st.caption("Go to Home / Browse Rooms tabs to find your next room")
        with t_c2:
            st.link_button("📩 Post Room Request", "#", use_container_width=True)
            st.caption("Go to Requests (Wanted) to post what you need")
        with t_c3:
            if st.button("🚚 Register as Driver", use_container_width=True):
                st.session_state.navigation = "Car Hire (Transport)"
                st.rerun()
            st.caption("Transport people & properties - Earn in Car Hire tab")
        st.divider()
        st.subheader("📋 Your Posted Room Requests - Private")
        my_reqs = [req for req in st.session_state.db.get("requests", []) if req.get("posted_by_phone") == user_phone_clean]
        my_student_reqs = [req for req in st.session_state.db.get("student_requests", []) if req.get("posted_by_phone") == user_phone_clean]
        if not my_reqs and not my_student_reqs:
            st.info("🔒 Private: No requests yet - Post in Requests (Wanted) tab")
        else:
            for req in my_reqs:
                with st.container(border=True):
                    cd = format_countdown((datetime.fromisoformat(req['created_at']) + timedelta(days=21)).isoformat()) if req.get('created_at') else None
                    if cd: st.markdown(f'<div class="countdown-badge">{cd}</div>', unsafe_allow_html=True)
                    st.write(f"**{req['loc']}** | **${req['budget']}** | {req.get('type','')}")
                    if st.button("Delete Request 🗑️", key=f"del_req_{req.get('id')}"):
                        st.session_state.db["requests"] = [r for r in st.session_state.db["requests"] if r.get("id")!= req.get("id")]; save_persistent_db(st.session_state.db); st.rerun()
            for req in my_student_reqs:
                with st.container(border=True):
                    st.write(f"🎓 **{req['name']} - {req['school']}** | **${req['budget']}**")
                    if st.button("Delete Student Request 🗑️", key=f"del_sreq_{req.get('id')}"):
                        st.session_state.db["student_requests"] = [r for r in st.session_state.db["student_requests"] if r.get("id")!= req.get("id")]; save_persistent_db(st.session_state.db); st.rerun()
        st.divider()
        st.subheader("🚚 Your Driver Listings (If Any)")
        my_drivers = [d for d in st.session_state.db.get("car_hire", []) if d.get("posted_by_phone") == user_phone_clean]
        if not my_drivers:
            st.info("No driver listings yet. Register in Car Hire tab to earn!")
        else:
            for d in my_drivers:
                with st.container(border=True):
                    st.write(f"**{d['name']}** - {d['vtype']} | {d['area']} | {format_countdown(d.get('expires_at'))}")
                    v_imgs = d.get("vehicle_imgs") or ([d.get("vehicle_img")] if d.get("vehicle_img") else [])
                    if v_imgs:
                        st.image(v_imgs[0], width=200)
    else:
        dash_t1, dash_t2, dash_t3, dash_t4, dash_t5 = st.tabs(["📦 Manage Packages","🏠 Standard Rooms","🎓 Student Housing","🏠 Houses / Stands Sale","🚚 Car Hire"])
        with dash_t1:
            st.subheader("📦 Your Packages - Private")
            my_active_pkgs = [p for p in st.session_state.db.get("approved_payments", []) if p.get("account_phone") == user_phone_clean]
            if not my_active_pkgs: st.info("🔒 Private: No active packages")
            else:
                for pkg in my_active_pkgs:
                    ft = pkg.get("feature_target") or {}
                    target_title = ft.get("title") if isinstance(ft, dict) and ft.get("title") else "Account Package"
                    app_at = pkg.get("approved_at") or pkg.get("submitted_at")
                    countdown = format_countdown((datetime.fromisoformat(app_at) + timedelta(days=pkg.get("package_days", 30))).isoformat()) if app_at else "Active"
                    with st.container(border=True):
                        st.markdown(f"### 💷 {pkg.get('package_name')} - ${pkg.get('package_price')}")
                        st.write(f"🏠 {target_title} | 🔑 {pkg.get('reference')}")
                        st.markdown(f'<div class="countdown-badge">{countdown}</div>', unsafe_allow_html=True)
        with dash_t2: st.subheader("🏠 Manage Standard Rooms - Private"); render_landlord_manage_section_fixed("rooms", "Standard Room")
        with dash_t3: st.subheader("🎓 Manage Student Housing - Private"); render_landlord_manage_section_fixed("student_rooms", "Student Accommodation")
        with dash_t4: st.subheader("🏠 Manage Houses Sale - Private"); render_landlord_manage_section_fixed("houses_sale", "House Sale")
        with dash_t5: st.subheader("🚚 Manage Car Hire - Private"); render_landlord_manage_section_fixed("car_hire", "Car Hire")

elif selected_tab == "Contact":
    st.title("📞 Contact Us & Support")
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.subheader("💬 Official Customer Support")
            st.write("📱 WhatsApp: 071 218 1037")
            st.write("📞 Direct Calls: 078 985 1813")
            st.link_button("💬 Chat on WhatsApp Direct", "https://wa.me/263712181037", use_container_width=True)
    with col2:
        with st.container(border=True):
            st.subheader("🛡️ Middleman Service")
            st.write("Middleman Fee: $35 USD")
            st.write("Verification & Safe Escrow")
    st.divider(); render_middleman_banner()

elif selected_tab.startswith("Admin Panel"):
    if not is_owner():
        st.error("⛔ Access Denied - Admin only Lewis G Kajayi (078 985 1813 / 071 218 1037)"); st.stop()
    # ===== ADMIN MESSAGE APP STYLE NOTIFICATIONS =====
    pending_count = len(st.session_state.db.get("pending_payments", []))
    if pending_count > 0:
        st.markdown(f"""
        <div style="position:fixed; top:70px; right:20px; z-index:9999; background:linear-gradient(135deg,#F59E0B 0%,#D97706 100%); color:white; padding:14px 20px; border-radius:12px; box-shadow:0 8px 24px rgba(245,158,11,0.45); border:2px solid #FDE68A; max-width:340px;">
            <p style="margin:0; font-weight:900; font-size:15px;">🔔 Admin: {pending_count} Payment{'s' if pending_count>1 else ''} Pending Verification!</p>
            <p style="margin:4px 0 0 0; font-size:11px; font-weight:600;">Tap Payments Approval tab to verify - Users waiting!</p>
        </div>
        """, unsafe_allow_html=True)
        st.toast(f"🔔 Admin Alert: {pending_count} pending payments need verification!", icon="🔔")
    # Show admin free unlimited badge
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0F172A 0%,#1E40AF 100%); border:2px solid #00FF88; border-radius:12px; padding:12px; margin-bottom:12px;">
        <p style="color:#00FF88 !important; font-weight:900; margin:0; font-size:14px;">👑 Admin Mode: Lewis G Kajayi - Unlimited FREE Access</p>
        <p style="color:#FFFFFF !important; font-size:11px; margin:4px 0 0 0;">All listings free, bypass button visible on Payments, all features unlocked</p>
    </div>
    """, unsafe_allow_html=True)
    if not st.session_state.admin_authenticated:
        st.title("🔒 Admin Authentication Required")
        with st.container(border=True):
            st.subheader("Enter Admin Credentials")
            pwd_input = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="collapsed")
            if st.button("Unlock", use_container_width=True, type="primary"):
                if pwd_input == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                    st.success("✅ Access Granted"); st.rerun()
                else: st.error("❌ Incorrect password")
        st.stop()
    st.title("👑 Admin Control Panel - Message Style Notifications")

    # ===== AUTO MARK ADMIN AS SEEN LIKE WHATSAPP =====
    # When admin opens Admin Panel, all pending ids are marked as read after 1.5s
    # so badge disappears until new payment arrives
    if "admin_panel_opened_at" not in st.session_state:
        st.session_state.admin_panel_opened_at = None
    if st.session_state.admin_panel_opened_at is None:
        st.session_state.admin_panel_opened_at = datetime.now()
    st.session_state.last_opened_tab = "Admin Panel"
    admin_elapsed = (datetime.now() - st.session_state.admin_panel_opened_at).total_seconds()
    if admin_elapsed > 1.5:
        all_admin_ids = [p.get("id") for p in st.session_state.db.get("pending_payments", [])]
        if all_admin_ids:
            st.session_state.seen_payment_ids.update(all_admin_ids)
    
    st.caption("💬 Works like WhatsApp - new payments show 🔵, after opening Admin Panel they mark as read")
    if st.button("Lock Admin Panel 🔒"): st.session_state.admin_authenticated = False; st.rerun()
    adm_t1, adm_t2, adm_t3, adm_t4 = st.tabs(["🚨 Pending Payments 🔵","✅ Approved Payments","👥 Users & Limits","🏠 Manage All Listings"])
    with adm_t1:
        st.subheader("🚨 Pending EcoCash Payments - Inbox Style")
        pending_list = st.session_state.db.get("pending_payments", [])
        if not pending_list: st.info("No pending payments - inbox empty")
        else:
            st.warning(f"🚨 {len(pending_list)} payment(s) - unread: {len([p for p in pending_list if p.get('id') not in st.session_state.seen_payment_ids])}")
            for p_idx, p_item in enumerate(list(pending_list)):
                is_unread = p_item.get("id") not in st.session_state.seen_payment_ids
                unread_marker = "🔵 NEW MESSAGE" if is_unread else "✅ Seen"
                with st.container(border=True):
                    st.markdown(f"**{unread_marker}** - {p_item.get('payer_name')} - {p_item.get('package_name')} (${p_item.get('package_price')})")
                    col1, col2 = st.columns([3,1])
                    with col1:
                        st.caption(f"Account: {p_item.get('account_name')} ({p_item.get('account_phone')}) | Submitted: {p_item.get('submitted_at','')[:19]}")
                        st.code(f"{p_item.get('reference')}")
                        ft = p_item.get("feature_target") or {}
                        if ft: st.caption(f"Target: {ft.get('title')} [{ft.get('db_key')}]")
                    with col2:
                        if st.button("✅ Approve", key=f"app_pay_{p_idx}", type="primary", use_container_width=True):
                            p_item["status"] = "Verified & Approved"; p_item["approved_at"] = datetime.now().isoformat(); p_item["needs_correction"] = False
                            st.session_state.db["approved_payments"].append(p_item); st.session_state.db["verified_references"].append(p_item.get("reference")); st.session_state.db["pending_payments"].remove(p_item)
                            activate_payment_package(p_item); save_persistent_db(st.session_state.db)
                            st.toast(f"✅ Approved {p_item.get('payer_name')}", icon="✅"); st.rerun()
                        if st.button("✏️ Wrong Ref", key=f"correct_pay_{p_idx}", use_container_width=True):
                            p_item["needs_correction"] = True
                            p_item["correction_message"] = "❌ Wrong code! Please put EXACT EcoCash code e.g. PP230510.1241.A12345"
                            save_persistent_db(st.session_state.db); st.toast("User notified", icon="📩"); st.rerun()
                        if st.button("❌ Reject", key=f"rej_pay_{p_idx}", use_container_width=True):
                            st.session_state.db["pending_payments"].remove(p_item); save_persistent_db(st.session_state.db); st.rerun()
    with adm_t2:
        st.subheader("✅ Approved Payments")
        app_list = st.session_state.db.get("approved_payments", [])
        if not app_list: st.info("No approved payments.")
        else:
            cats = ["All Categories"] + sorted(list(set([p.get("package_name","Unknown") for p in app_list])))
            selected_cat = st.selectbox("📦 Filter by Package Category", cats, key="approved_cat_filter")
            filtered = app_list if selected_cat == "All Categories" else [p for p in app_list if p.get("package_name") == selected_cat]
            for idx, pay in enumerate(reversed(filtered)):
                app_at_str = pay.get("approved_at") or pay.get("submitted_at") or ""
                try:
                    app_dt = datetime.fromisoformat(app_at_str)
                    exp_dt = app_dt + timedelta(days=pay.get("package_days", 30))
                    exp_formatted = exp_dt.strftime("%Y-%m-%d %H:%M"); countdown = format_countdown(exp_dt.isoformat()) or "Active"; app_formatted = app_dt.strftime("%Y-%m-%d %H:%M")
                except: exp_formatted = "N/A"; countdown = "Active"; app_formatted = app_at_str[:16]
                with st.container(border=True):
                    st.markdown(f"**{pay.get('payer_name')}** | {pay.get('package_name')} | ${pay.get('package_price')}")
                    c1,c2,c3 = st.columns([2,2,2])
                    with c1: st.caption("EcoCash Reference"); st.code(pay.get("reference","N/A")); st.caption(f"👥 {pay.get('account_name')} ({pay.get('account_phone')})")
                    with c2: st.caption("📅 Approved At"); st.write(app_formatted); st.caption("⏰ Ends At"); st.write(f"**{exp_formatted}**")
                    with c3:
                        st.markdown(f'<div class="countdown-badge">{countdown}</div>', unsafe_allow_html=True)
                        ft = pay.get("feature_target") or {}
                        if ft: st.caption(f"🏠 {ft.get('title','')}")
                        if st.button(f"💥 Deplete Now", key=f"deplete_approved_{pay.get('id')}_{idx}", type="primary", use_container_width=True):
                            deplete_package(pay)
                            st.session_state.db["approved_payments"] = [p for p in st.session_state.db["approved_payments"] if p.get("id")!= pay.get("id")]
                            save_persistent_db(st.session_state.db); st.toast("Depleted"); st.rerun()
    with adm_t3:
        st.subheader("👥 Users & Limits")
        users_list = st.session_state.db.get("users", [])
        landlords = [u for u in users_list if u.get("role") == "Landlord"]
        tenants = [u for u in users_list if u.get("role")!= "Landlord"]
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total People", len(users_list))
        with c2: st.metric("🏠 Landlords", len(landlords))
        with c3: st.metric("👥 Tenants", len(tenants))
        st.dataframe(pd.DataFrame(users_list))
    with adm_t4:
        st.subheader("🏠 Manage All Listings - Admin Full Power")
        all_cats = ["rooms", "student_rooms", "houses_sale", "car_hire", "requests", "student_requests"]
        cat_choice = st.selectbox("📨 Category", all_cats, key="admin_manage_cat")
        items = st.session_state.db.get(cat_choice, [])
        if not items: st.info(f"No items in {cat_choice}")
        else:
            st.write(f"Total: {len(items)} listings")
            for idx, item in enumerate(list(items)):
                with st.container(border=True):
                    st.write(f"**{item.get('title', item.get('name'))}** - By: {item.get('posted_by_phone')} | {item.get('posted_by_name')} | {format_countdown(item.get('expires_at'))}")
                    if st.button(f"Delete 🗑️ Admin Delete", key=f"adm_del_{cat_choice}_{idx}", type="primary"):
                        del_id = item.get("id")
                        st.session_state.db[cat_choice] = [x for x in st.session_state.db[cat_choice] if x.get("id")!= del_id]
                        for hi in range(len(st.session_state.db.get("hot_deals",[]))):
                            hd = st.session_state.db["hot_deals"][hi]
                            if hd and hd.get("id") == del_id: st.session_state.db["hot_deals"][hi] = None
                        save_persistent_db(st.session_state.db); st.toast("Deleted by Admin"); st.rerun()
                st.divider()


# ===== GLOBAL FOOTER - FIXED - NO BLACK/GREY - MATCHES LOGO STYLE =====
st.markdown("<br><br>", unsafe_allow_html=True)
st.divider()
st.markdown('''
<div class="gella-footer-fixed">
    <p class="logo-pill">Gella Enterprises Pvt Ltd</p>
    <p style='color:#FEF08A !important; font-size:12px; font-weight:800; margin:12px 0 0 0; letter-spacing:0.6px; text-transform:uppercase;'>Secure • Verified • Trusted Platform</p>
    <p style='color:#0F172A !important; font-size:13px; font-weight:900; margin:14px 0 0 0; background:#FFFFFF !important; padding:8px 18px; border-radius:10px; border:1.5px solid #CBD5E1; display:inline-block; -webkit-text-fill-color:#0F172A !important;'>© 2026 Mutare Room Finder. All Rights Reserved.</p>
    <p style='color:#FFFFFF !important; font-size:11px; font-weight:700; margin:10px 0 0 0; text-shadow:0 1px 2px rgba(0,0,0,0.4);'>Why 1000+ Users Trust Us: Verified landlords • EcoCash secure payments • 21-day fresh listings • Admin approved • Instant WhatsApp contact</p>
</div>
''', unsafe_allow_html=True)
