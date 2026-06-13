"""
Dashboard BI ISPU DKI Jakarta
Tugas 6 - Business Intelligence Dashboard

Run:
    streamlit run app.py
"""

from __future__ import annotations

from html import escape as html_escape
from pathlib import Path
from textwrap import dedent
from typing import Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =============================================================================
# PAGE CONFIG
# =============================================================================

st.set_page_config(
    page_title="Dashboard BI ISPU Jakarta",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# DESIGN TOKENS
# =============================================================================

APP_TITLE = "Observatorium Langit Udara Jakarta"
APP_SUBTITLE = (
    "Dashboard keputusan kualitas udara: membaca napas kota, sinyal risiko, "
    "lokasi prioritas, pencemar dominan, periode rawan, dan kepercayaan data."
)

CATEGORY_ORDER = ["BAIK", "SEDANG", "TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"]
CATEGORY_COLORS = {
    "BAIK": "#00A676",
    "SEDANG": "#F4B400",
    "TIDAK SEHAT": "#F97316",
    "SANGAT TIDAK SEHAT": "#E11D48",
    "BERBAHAYA": "#7C3AED",
    "TIDAK ADA DATA": "#64748B",
    "LAINNYA": "#475569",
}

CRITICAL_COLORS = {
    "PM10": "#0284C7",
    "PM25": "#16A34A",
    "SO2": "#CA8A04",
    "CO": "#EA580C",
    "O3": "#7C3AED",
    "NO2": "#DB2777",
    "LAINNYA": "#475569",
}

RISK_COLORS = {
    "Prioritas Tinggi": "#E11D48",
    "Prioritas Menengah": "#F97316",
    "Prioritas Pemantauan": "#00A676",
    "Tidak Ada Data": "#64748B",
}

POLLUTANT_COLS = ["pm10", "pm25", "so2", "co", "o3", "no2"]
MONTH_ORDER = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember"
]

MENU_ITEMS = [
    "Overview Kualitas Udara",
    "Tren Temporal",
    "Perbandingan Stasiun",
    "Pencemar Kritis",
    "Pola Musiman",
    "Data Quality / Audit Trail",
]

# Plotly toolbar can overlap titles on Streamlit Cloud screenshots.
# Hide it by default; users still get hover tooltips and interaction.
PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


PAGE_PURPOSE = {
    "Overview Kualitas Udara": "Kondisi terkini dan prioritas cepat untuk keputusan pimpinan.",
    "Tren Temporal": "Arah perubahan kualitas udara dan periode yang melewati ambang risiko.",
    "Perbandingan Stasiun": "Lokasi prioritas pengendalian berdasarkan frekuensi risiko.",
    "Pencemar Kritis": "Parameter pencemar yang paling perlu dikendalikan.",
    "Pola Musiman": "Kalender antisipasi periode rawan kualitas udara.",
    "Data Quality / Audit Trail": "Kepercayaan data, batasan interpretasi, dan jejak validasi.",
}

# Koordinat aproksimasi titik SPKU untuk visualisasi peta.
# Peta digunakan sebagai konteks lokasi stasiun pemantau, bukan sebagai
# interpolasi/pewarnaan seluruh wilayah Jakarta.
STATION_COORDINATES = {
    "DKI1": {
        "lat": -6.19445,
        "lon": 106.82310,
        "lokasi_ringkas": "Bundaran HI",
        "wilayah": "Jakarta Pusat",
    },
    "DKI2": {
        "lat": -6.16035,
        "lon": 106.90445,
        "lokasi_ringkas": "Kelapa Gading",
        "wilayah": "Jakarta Utara",
    },
    "DKI3": {
        "lat": -6.33410,
        "lon": 106.82390,
        "lokasi_ringkas": "Jagakarsa",
        "wilayah": "Jakarta Selatan",
    },
    "DKI4": {
        "lat": -6.29020,
        "lon": 106.90520,
        "lokasi_ringkas": "Lubang Buaya",
        "wilayah": "Jakarta Timur",
    },
    "DKI5": {
        "lat": -6.20740,
        "lon": 106.76910,
        "lokasi_ringkas": "Kebon Jeruk",
        "wilayah": "Jakarta Barat",
    },
}


# Peristiwa/konteks penting untuk anotasi tren.
# Catatan metodologis: anotasi hanya memberi konteks interpretasi, bukan klaim sebab-akibat.
CONTEXT_EVENTS = {
    "covid_start": pd.Timestamp("2020-03-01"),
    "covid_end": pd.Timestamp("2021-12-31"),
    "covid_label": "COVID-19 / pembatasan aktivitas (konteks, bukan kausal)",
}

# =============================================================================
# CSS
# =============================================================================

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

:root {
    --paper: #F7FBFF;
    --paper-warm: #FFF7ED;
    --surface: #FFFFFF;
    --surface-soft: #F8FAFC;
    --surface-blue: #EAF6FF;
    --surface-green: #ECFDF5;
    --surface-yellow: #FFF7D6;
    --surface-orange: #FFF1E8;
    --surface-red: #FFF1F3;
    --surface-violet: #F3EEFF;
    --ink: #102033;
    --ink-2: #1E3448;
    --slate: #334155;
    --muted: #5B6B7C;
    --line: rgba(15, 23, 42, 0.12);
    --line-strong: rgba(15, 23, 42, 0.20);
    --blue: #0284C7;
    --cyan: #0891B2;
    --leaf: #00A676;
    --yellow: #F4B400;
    --orange: #F97316;
    --red: #E11D48;
    --violet: #7C3AED;
    --pink: #DB2777;
    --teal: #0F766E;
    --shadow: 0 18px 46px rgba(15, 23, 42, .10);
    --shadow-soft: 0 10px 28px rgba(15, 23, 42, .075);
}

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

.stApp {
    color: var(--ink);
    background:
        radial-gradient(circle at 8% -8%, rgba(2,132,199,.20), transparent 32%),
        radial-gradient(circle at 86% 4%, rgba(249,115,22,.18), transparent 30%),
        radial-gradient(circle at 12% 102%, rgba(0,166,118,.18), transparent 32%),
        linear-gradient(135deg, #F7FBFF 0%, #EDF7FF 38%, #FFF7ED 74%, #F8FAFC 100%);
    overflow-x: hidden;
}

/* Atmosfer ringan: cukup berwarna, tetapi konten tetap di atas permukaan putih berkontras tinggi. */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: 0;
    pointer-events: none;
    background-image:
        radial-gradient(circle at 22% 20%, rgba(16,32,51,.065) 0 1px, transparent 1.7px),
        radial-gradient(circle at 78% 42%, rgba(249,115,22,.12) 0 1px, transparent 1.9px),
        linear-gradient(118deg, transparent 0%, rgba(2,132,199,.105) 28%, transparent 48%, rgba(0,166,118,.095) 72%, transparent 100%);
    background-size: 54px 54px, 78px 78px, 100% 100%;
    opacity: .65;
}

.stApp::after {
    content: "";
    position: fixed;
    left: -10vw;
    right: -10vw;
    top: 130px;
    height: 190px;
    z-index: 0;
    pointer-events: none;
    opacity: .26;
    background:
        repeating-linear-gradient(168deg, transparent 0 28px, rgba(2,132,199,.18) 29px 31px, transparent 32px 70px),
        radial-gradient(ellipse at 64% 44%, rgba(255,255,255,.78), transparent 62%);
    transform: rotate(-1.4deg);
}

.block-container, [data-testid="stSidebar"] { position: relative; z-index: 2; }
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 3.25rem;
    max-width: 1540px;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(255,255,255,.98), rgba(248,250,252,.98));
    border-right: 1px solid var(--line-strong);
    box-shadow: 16px 0 44px rgba(15,23,42,.07);
}
[data-testid="stSidebar"] * { color: var(--ink) !important; }
[data-testid="stSidebar"] h3 {
    font-family: 'Barlow Condensed', 'Inter', sans-serif;
    text-transform: uppercase;
    letter-spacing: .02em;
}

h1, h2, h3, h4 {
    font-family: 'Barlow Condensed', 'Inter', system-ui, sans-serif;
    letter-spacing: .005em;
    color: var(--ink) !important;
}
p, li, span, label, div { color: inherit; }
a { color: #075985 !important; font-weight: 700; }
hr { border: none; border-top: 1px solid var(--line); margin: 1.35rem 0; }

.command-hero {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(15,23,42,.14);
    border-radius: 24px;
    padding: 16px 20px 16px 20px;
    background:
        linear-gradient(135deg, rgba(255,255,255,.96), rgba(255,255,255,.88)),
        radial-gradient(circle at 8% 10%, rgba(2,132,199,.32), transparent 35%),
        radial-gradient(circle at 88% 8%, rgba(249,115,22,.24), transparent 34%),
        radial-gradient(circle at 72% 108%, rgba(0,166,118,.22), transparent 38%);
    box-shadow: var(--shadow), inset 0 1px 0 rgba(255,255,255,.92);
}
.command-hero::before {
    content: "";
    position: absolute;
    left: -8%; right: -8%; bottom: -30px;
    height: 78px;
    background: linear-gradient(90deg, #00A676 0%, #0284C7 22%, #F4B400 47%, #F97316 66%, #E11D48 83%, #7C3AED 100%);
    filter: blur(30px);
    opacity: .32;
    pointer-events: none;
}
.command-hero::after {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(circle at 77% 15%, rgba(16,32,51,.07) 0 1px, transparent 1.8px),
        radial-gradient(circle at 68% 58%, rgba(249,115,22,.13) 0 1px, transparent 2px),
        repeating-linear-gradient(12deg, transparent 0 20px, rgba(2,132,199,.11) 21px 22px, transparent 23px 48px);
    background-size: 42px 42px, 58px 58px, 100% 100%;
    mask-image: linear-gradient(90deg, rgba(0,0,0,.56), transparent 88%);
    opacity: .50;
    pointer-events: none;
}

.hero-grid { position: relative; z-index: 2; display: grid; grid-template-columns: minmax(0, 1fr) auto; gap: 18px; align-items: end; }
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 8px;
    color: #064E3B !important;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: .72rem; font-weight: 800; letter-spacing: .16em;
    margin-bottom: 8px;
}
.hero-eyebrow::before { content: ""; width: 36px; height: 10px; border-radius: 999px; background: linear-gradient(90deg, var(--leaf), var(--blue), var(--yellow), var(--orange), var(--red), var(--violet)); box-shadow: 0 0 18px rgba(2,132,199,.20); }
.hero-title { font-family: 'Barlow Condensed', 'Inter', sans-serif; font-size: clamp(1.72rem, 2.48vw, 2.92rem); line-height: .94; letter-spacing: .012em; text-transform: uppercase; margin: 0; max-width: 980px; text-wrap: balance; color: var(--ink) !important; }
.hero-copy { margin-top: 8px; color: var(--slate) !important; max-width: 900px; font-size: .91rem; line-height: 1.55; font-weight: 500; }
.hero-meta { min-width: 286px; border: 1px solid var(--line); border-radius: 20px; background: rgba(255,255,255,.94); backdrop-filter: blur(18px); padding: 13px 15px; box-shadow: inset 0 1px 0 rgba(255,255,255,.90), var(--shadow-soft); }
.hero-meta .label { color: var(--muted) !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: .70rem; letter-spacing: .12em; text-transform: uppercase; font-weight: 800; }
.hero-meta .value { font-family: 'Barlow Condensed', 'Inter', sans-serif; font-size: 1.08rem; line-height: 1.08; color: var(--ink) !important; margin-top: 5px; }
.hero-meta .status { display: inline-flex; margin-top: 10px; padding: 7px 10px; border-radius: 999px; border: 1px solid rgba(0,166,118,.34); color: #064E3B !important; background: rgba(0,166,118,.13); font-weight: 800; font-size: .74rem; }
.hero-meta .data-badge { display: inline-flex; margin-top: 8px; padding: 7px 10px; border-radius: 999px; border: 1px solid rgba(202,138,4,.34); color: #4A3411 !important; background: #FFF7D6; font-weight: 900; font-size: .72rem; }
.hero-meta .obs-badge { display: inline-flex; margin-top: 8px; margin-right: 6px; padding: 7px 10px; border-radius: 999px; border: 1px solid rgba(2,132,199,.32); color: #075985 !important; background: #EAF6FF; font-weight: 900; font-size: .72rem; }
.hero-meta .badge-line { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
.hero-meta .badge-line .status, .hero-meta .badge-line .obs-badge, .hero-meta .badge-line .data-badge { margin-top: 0; }

.section-title { display: flex; align-items: center; gap: 12px; margin: 1.55rem 0 .80rem 0; }
.section-title .bar { width: 48px; height: 12px; border-radius: 999px; background: linear-gradient(90deg, var(--leaf), var(--blue), var(--yellow), var(--orange)); box-shadow: 0 0 18px rgba(2,132,199,.16); }
.section-title h3 { margin: 0; font-size: 1.52rem; text-transform: uppercase; letter-spacing: .018em; }

.kpi-card { position: relative; min-height: 145px; padding: 19px 18px 17px 18px; border: 1px solid var(--line); border-radius: 26px; background: #FFFFFF; box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.92); overflow: hidden; }
.kpi-card::before { content:""; position: absolute; right: -38px; top: -46px; width: 142px; height: 142px; border-radius: 999px; background: color-mix(in srgb, var(--accent, #0284C7) 24%, transparent); filter: blur(12px); opacity: .88; }
.kpi-card::after { content:""; position: absolute; left: 0; right: 0; top: 0; height: 6px; background: linear-gradient(90deg, var(--accent, #0284C7), rgba(255,255,255,.65)); }
.kpi-label { color: var(--muted) !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: .70rem; font-weight: 800; letter-spacing: .09em; text-transform: uppercase; }
.kpi-value { position: relative; z-index: 1; margin-top: 10px; color: var(--ink) !important; font-family: 'Barlow Condensed', 'Inter', sans-serif; font-size: clamp(1.80rem, 2.35vw, 2.65rem); font-weight: 800; line-height: .95; letter-spacing: .01em; }
.kpi-delta { position: relative; z-index: 1; margin-top: 12px; display: inline-flex; align-items: center; padding: 6px 9px; border-radius: 999px; background: #F1F5F9; border: 1px solid var(--line); color: var(--slate) !important; font-size: .78rem; font-weight: 800; }
.kpi-note { position: relative; z-index: 1; margin-top: 10px; color: var(--slate) !important; font-size: .80rem; line-height: 1.36; font-weight: 600; }

.glass-panel { border: 1px solid var(--line); border-radius: 28px; background: rgba(255,255,255,.92); box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.90); backdrop-filter: blur(10px); padding: 18px; margin-bottom: 1rem; }
.insight-panel { position: relative; border: 1px solid rgba(2,132,199,.22); border-left: 0; border-radius: 24px; background: linear-gradient(135deg, #EAF6FF, #FFFFFF); padding: 18px 20px 18px 24px; margin: 1.08rem 0; overflow: hidden; box-shadow: var(--shadow-soft); }
.insight-panel::before { content: ""; position: absolute; left: 0; top: 14px; bottom: 14px; width: 6px; border-radius: 999px; background: linear-gradient(180deg, var(--blue), var(--leaf)); }
.insight-title { color: #075985 !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-weight: 800; letter-spacing: .10em; text-transform: uppercase; font-size: .72rem; margin-bottom: 8px; }
.insight-panel p { color: var(--ink) !important; margin: 0; line-height: 1.66; font-weight: 500; }
.warning-panel { border: 1px solid rgba(202,138,4,.28); border-left: 6px solid var(--yellow); border-radius: 22px; background: linear-gradient(135deg, #FFF7D6, #FFFFFF); padding: 16px 18px; margin: 1rem 0; box-shadow: var(--shadow-soft); }
.warning-panel p { margin: 0; color: #4A3411 !important; line-height: 1.58; font-weight: 600; }

.small-muted { color: var(--muted) !important; font-size: .84rem; line-height: 1.5; }

[data-testid="stMetric"] { background: #FFFFFF; border: 1px solid var(--line); border-radius: 20px; padding: 14px 16px; box-shadow: var(--shadow-soft); }
[data-testid="stMetric"] * { color: var(--ink) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 18px; overflow: hidden; box-shadow: var(--shadow-soft); background: #FFFFFF; }
.stButton button, .stDownloadButton button { border-radius: 16px !important; border: 1px solid rgba(2,132,199,.32) !important; background: linear-gradient(135deg, #FFFFFF, #EAF6FF) !important; color: var(--ink) !important; font-weight: 800 !important; box-shadow: var(--shadow-soft) !important; }
.stButton button:hover, .stDownloadButton button:hover { border-color: rgba(0,166,118,.48) !important; box-shadow: 0 14px 30px rgba(0,166,118,.12) !important; }
div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="base-input"] { background-color: #FFFFFF !important; border-color: var(--line-strong) !important; color: var(--ink) !important; }
div[data-baseweb="select"] *, div[data-baseweb="input"] *, div[data-baseweb="base-input"] * { color: var(--ink) !important; }
.stRadio [role="radiogroup"] { gap: 0.45rem; }
.stRadio label, .stCheckbox label { color: var(--ink) !important; }

/* Form control contrast hardening: Streamlit/BaseWeb sometimes injects light text
   into radio and checkbox labels. Force every label descendant to dark ink so
   options remain readable on the light air-quality background. */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stRadio"],
[data-testid="stRadio"] *,
[data-testid="stCheckbox"],
[data-testid="stCheckbox"] * {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    opacity: 1 !important;
    text-shadow: none !important;
}
[data-testid="stRadio"] label,
[data-testid="stRadio"] label *,
[data-testid="stCheckbox"] label,
[data-testid="stCheckbox"] label * {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
    font-weight: 750 !important;
}
[data-testid="stRadio"] p,
[data-testid="stRadio"] span,
[data-testid="stCheckbox"] p,
[data-testid="stCheckbox"] span {
    color: var(--ink) !important;
    -webkit-text-fill-color: var(--ink) !important;
}
[data-testid="stCheckbox"] div[role="checkbox"],
[data-testid="stRadio"] div[role="radio"] {
    color: var(--ink) !important;
    opacity: 1 !important;
}
[data-testid="stCheckbox"] label:hover *,
[data-testid="stRadio"] label:hover * {
    color: #075985 !important;
    -webkit-text-fill-color: #075985 !important;
}
button[data-baseweb="tab"] { font-weight: 800 !important; color: var(--slate) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--ink) !important; }
.streamlit-expanderHeader { font-weight: 800 !important; color: var(--ink) !important; }

.air-ribbon-wrap { position: relative; z-index: 2; margin-top: 10px; border-radius: 16px; padding: 9px 11px; background: #FFFFFF; border: 1px solid var(--line); box-shadow: 0 8px 20px rgba(15,23,42,.055); }
.air-ribbon-title { display: flex; justify-content: space-between; gap: 12px; color: var(--slate) !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-weight: 800; font-size: .67rem; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px; }
.air-ribbon { display: flex; width: 100%; overflow: hidden; height: 13px; border-radius: 999px; border: 1px solid rgba(15,23,42,.16); background: #FFFFFF; }
.air-ribbon-segment { height: 100%; min-width: 1.2%; }
.air-ribbon-legend { display: flex; flex-wrap: wrap; gap: 7px 12px; margin-top: 8px; color: var(--slate) !important; font-size: .69rem; font-weight: 800; }
.legend-dot { display: inline-flex; align-items: center; gap: 6px; color: var(--slate) !important; }
.legend-dot::before { content:""; width: 9px; height: 9px; border-radius: 999px; background: var(--dot); box-shadow: 0 0 0 3px rgba(15,23,42,.06); }
.page-brief {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    border-radius: 16px;
    padding: 10px 12px;
    margin: .72rem 0 .42rem 0;
    background: rgba(255,255,255,.90);
    border: 1px solid rgba(15,23,42,.11);
    color: var(--slate) !important;
    box-shadow: 0 8px 20px rgba(15,23,42,.055);
    font-size: .82rem;
    line-height: 1.42;
}
.page-brief::before {
    content: "";
    flex: 0 0 auto;
    width: 9px;
    height: 9px;
    margin-top: 6px;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--leaf), var(--blue), var(--yellow), var(--orange));
    box-shadow: 0 0 0 4px rgba(2,132,199,.10);
}
.page-brief .context-kicker {
    display: inline-block;
    margin-right: 7px;
    color: #075985 !important;
    font-family: 'JetBrains Mono', ui-monospace, monospace;
    font-size: .64rem;
    font-weight: 900;
    letter-spacing: .10em;
    text-transform: uppercase;
    white-space: nowrap;
}
.page-brief .context-body { color: #334155 !important; font-weight: 650; }
[data-testid="stPlotlyChart"] { border: 1px solid var(--line); border-radius: 24px; padding: 10px 10px 2px 10px; background: #FFFFFF; box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.88); }
.sidebar-purpose { margin: 8px 0 4px 0; border-radius: 18px; padding: 12px 13px; background: linear-gradient(135deg, #EAF6FF, #FFFFFF); border: 1px solid rgba(2,132,199,.22); color: var(--slate) !important; font-size: .82rem; line-height: 1.45; font-weight: 600; }
.empty-state-panel { border-radius: 24px; padding: 22px; border: 1px dashed rgba(225,29,72,.42); background: #FFFFFF; color: var(--ink) !important; box-shadow: var(--shadow-soft); }
.empty-state-panel * { color: var(--ink) !important; }

/* Plotly legend/readability hardening: keep legend titles, labels, axes, and chart titles dark on light cards. */
[data-testid="stPlotlyChart"] .legendtitletext,
[data-testid="stPlotlyChart"] .legendtext,
[data-testid="stPlotlyChart"] .gtitle,
[data-testid="stPlotlyChart"] .xtitle,
[data-testid="stPlotlyChart"] .ytitle,
[data-testid="stPlotlyChart"] .xtick text,
[data-testid="stPlotlyChart"] .ytick text {
    fill: #102033 !important;
    color: #102033 !important;
    opacity: 1 !important;
}
[data-testid="stPlotlyChart"] .legendtitletext {
    font-weight: 900 !important;
}
[data-testid="stPlotlyChart"] .colorbar text,
[data-testid="stPlotlyChart"] .cbtitle,
[data-testid="stPlotlyChart"] .cbaxis text {
    fill: #102033 !important;
    color: #102033 !important;
    opacity: 1 !important;
    font-weight: 800 !important;
}

/* Readability hardening: anything inside custom panels must stay dark, never pastel-on-pastel. */
.command-hero *, .kpi-card *, .glass-panel *, .insight-panel *, .warning-panel *, .air-ribbon-wrap *, .page-brief *, .sidebar-purpose * { text-shadow: none !important; }

@media (max-width: 980px) {
    .hero-grid { grid-template-columns: 1fr; }
    .hero-meta { min-width: unset; }
    .command-hero { padding: 24px 22px; border-radius: 26px; }
}


/* Light executive tables: replace Streamlit's dark dataframe renderer for decision tables. */
.light-table-wrap {
    width: 100%;
    overflow: auto;
    border-radius: 22px;
    border: 1px solid rgba(15, 23, 42, .14);
    background: rgba(255,255,255,.96);
    box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.96);
    margin: .55rem 0 1.1rem 0;
}
.light-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    min-width: 920px;
    color: var(--ink);
    font-size: .88rem;
}
.light-table thead th {
    position: sticky;
    top: 0;
    z-index: 3;
    background: linear-gradient(180deg, #FFFFFF 0%, #F1F7FE 100%);
    color: #1E3448 !important;
    text-align: left;
    padding: 13px 12px;
    border-bottom: 1px solid #D7E3EF;
    border-right: 1px solid #E2E8F0;
    font-weight: 900;
    letter-spacing: .025em;
    white-space: nowrap;
}
.light-table tbody td {
    padding: 12px 12px;
    border-bottom: 1px solid #E4ECF5;
    border-right: 1px solid #EEF2F7;
    background: rgba(255,255,255,.96);
    color: #102033 !important;
    vertical-align: middle;
    font-weight: 650;
}
.light-table tbody tr:nth-child(even) td { background: #F8FBFF; }
.light-table tbody tr:hover td { background: #EEF8FF; }
.light-table tbody tr:last-child td { border-bottom: none; }
.light-table th:last-child, .light-table td:last-child { border-right: none; }
.light-table .num-cell { text-align: right; font-variant-numeric: tabular-nums; font-family: 'JetBrains Mono', ui-monospace, monospace; }
.light-table .long-cell { min-width: 260px; line-height: 1.45; white-space: normal; }
.light-table .nowrap-cell { white-space: nowrap; }
.light-progress { display: flex; align-items: center; gap: 10px; min-width: 164px; }
.light-progress-track {
    width: 106px;
    height: 10px;
    border-radius: 999px;
    overflow: hidden;
    background: #E8EEF5;
    border: 1px solid #D5E1EC;
}
.light-progress-fill { height: 100%; border-radius: 999px; background: var(--bar, #F97316); }
.light-progress-value { color: #102033 !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-weight: 900; font-size: .80rem; white-space: nowrap; }
.table-chip {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    border-radius: 999px;
    padding: 5px 9px;
    background: var(--chip-bg, #F8FAFC);
    border: 1px solid var(--chip-border, #CBD5E1);
    color: var(--chip-ink, #102033) !important;
    font-weight: 900;
    font-size: .78rem;
    white-space: nowrap;
}
.table-chip::before {
    content: "";
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: var(--chip-dot, #64748B);
}
.table-note { margin: -0.45rem 0 1rem 0; color: var(--muted) !important; font-size: .80rem; font-weight: 650; }


/* Jakarta identity watermark: subtle Monas + skyline, placed behind data components. */
.block-container::after {
    content: "";
    position: fixed;
    left: clamp(240px, 18vw, 330px);
    right: 0;
    bottom: 0;
    height: 178px;
    z-index: 0;
    pointer-events: none;
    opacity: .72;
    background-image:
        linear-gradient(to top, rgba(247,251,255,.96) 0%, rgba(247,251,255,.78) 28%, rgba(247,251,255,.34) 64%, rgba(247,251,255,0) 100%),
        url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNDAwIDI2MCIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNYXggbWVldCI+CiAgPGRlZnM+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9InNreSIgeDE9IjAiIHgyPSIxIiB5MT0iMCIgeTI9IjAiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiM1RTdGOTYiIHN0b3Atb3BhY2l0eT0iMC4xNiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjAuMzQiIHN0b3AtY29sb3I9IiMyRTVGODAiIHN0b3Atb3BhY2l0eT0iMC4yMiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjAuNjQiIHN0b3AtY29sb3I9IiM3REFBOTIiIHN0b3Atb3BhY2l0eT0iMC4xNSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNDOEEyNEQiIHN0b3Atb3BhY2l0eT0iMC4xMiIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZ29sZCIgeDE9IjAiIHgyPSIwIiB5MT0iMCIgeTI9IjEiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiNDOEEyNEQiIHN0b3Atb3BhY2l0eT0iMC4yOCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNDOEEyNEQiIHN0b3Atb3BhY2l0eT0iMC4wOCIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICA8L2RlZnM+CiAgPHBhdGggZD0iTTAgMjI5IEMxMTAgMjE2IDIxMCAyMTggMzE1IDIyNCBDNDMwIDIzMCA1MjAgMjEwIDYzMiAyMTggQzc1NiAyMjggODcwIDIxNCA5ODkgMjIwIEMxMTEwIDIyNiAxMjQwIDIxMCAxNDAwIDIyMCBMMTQwMCAyNjAgTDAgMjYwIFoiIGZpbGw9IiNGRkZGRkYiIGZpbGwtb3BhY2l0eT0iMC43MiIvPgogIDxnIGZpbGw9InVybCgjc2t5KSI+CiAgICA8cmVjdCB4PSIxMiIgeT0iMTY0IiB3aWR0aD0iNDIiIGhlaWdodD0iNzIiIHJ4PSIzIi8+CiAgICA8cmVjdCB4PSI2MiIgeT0iMTM0IiB3aWR0aD0iNTgiIGhlaWdodD0iMTAyIiByeD0iNCIvPgogICAgPHJlY3QgeD0iMTMwIiB5PSIxNTQiIHdpZHRoPSI0OCIgaGVpZ2h0PSI4MiIgcng9IjMiLz4KICAgIDxyZWN0IHg9IjE5MCIgeT0iMTEyIiB3aWR0aD0iNzAiIGhlaWdodD0iMTI0IiByeD0iNSIvPgogICAgPHBhdGggZD0iTTI3NiAyMzYgTDI3NiAxMTggTDMxOCAxMTggTDMxOCA5OCBMMzUwIDk4IEwzNTAgMjM2IFoiLz4KICAgIDxyZWN0IHg9IjM2NiIgeT0iMTQ1IiB3aWR0aD0iNDgiIGhlaWdodD0iOTEiIHJ4PSIzIi8+CiAgICA8cmVjdCB4PSI0MjYiIHk9IjkyIiB3aWR0aD0iNzQiIGhlaWdodD0iMTQ0IiByeD0iNSIvPgogICAgPHJlY3QgeD0iNTEyIiB5PSIxMjgiIHdpZHRoPSI1NCIgaGVpZ2h0PSIxMDgiIHJ4PSI0Ii8+CiAgICA8cGF0aCBkPSJNNTg4IDIzNiBMNTg4IDE2NCBMNjI1IDEzMiBMNjYyIDE2NCBMNjYyIDIzNiBaIi8+CiAgICA8cmVjdCB4PSI2NzYiIHk9IjE1MCIgd2lkdGg9IjYwIiBoZWlnaHQ9Ijg2IiByeD0iNCIvPgogICAgPHJlY3QgeD0iNzU0IiB5PSI5MiIgd2lkdGg9IjcyIiBoZWlnaHQ9IjE0NCIgcng9IjUiLz4KICAgIDxyZWN0IHg9Ijg0MCIgeT0iMTI4IiB3aWR0aD0iNDYiIGhlaWdodD0iMTA4IiByeD0iMyIvPgogICAgPHJlY3QgeD0iOTAwIiB5PSIxNTYiIHdpZHRoPSI3OCIgaGVpZ2h0PSI4MCIgcng9IjQiLz4KICAgIDxyZWN0IHg9Ijk5NCIgeT0iMTEwIiB3aWR0aD0iNjAiIGhlaWdodD0iMTI2IiByeD0iNSIvPgogICAgPHJlY3QgeD0iMTA2NiIgeT0iMTQyIiB3aWR0aD0iNTYiIGhlaWdodD0iOTQiIHJ4PSI0Ii8+CiAgICA8cmVjdCB4PSIxMTM2IiB5PSIxMjAiIHdpZHRoPSI3MiIgaGVpZ2h0PSIxMTYiIHJ4PSI1Ii8+CiAgICA8cmVjdCB4PSIxMjIyIiB5PSIxNTYiIHdpZHRoPSI1MiIgaGVpZ2h0PSI4MCIgcng9IjMiLz4KICAgIDxyZWN0IHg9IjEyODgiIHk9IjEzNCIgd2lkdGg9Ijc4IiBoZWlnaHQ9IjEwMiIgcng9IjUiLz4KICA8L2c+CiAgPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNjUwIDApIj4KICAgIDxwYXRoIGQ9Ik00OCAyMzYgTDU2IDEwMSBMNjUgMjM2IFoiIGZpbGw9InVybCgjZ29sZCkiLz4KICAgIDxwYXRoIGQ9Ik02MCA5MiBMNjQgNTQgTDY4IDkyIFoiIGZpbGw9IiNDOEEyNEQiIGZpbGwtb3BhY2l0eT0iMC4yNSIvPgogICAgPGNpcmNsZSBjeD0iNjQiIGN5PSIxMDMiIHI9IjE3IiBmaWxsPSIjQzhBMjREIiBmaWxsLW9wYWNpdHk9IjAuMTMiLz4KICAgIDxyZWN0IHg9IjQ2IiB5PSIyMjQiIHdpZHRoPSIzOCIgaGVpZ2h0PSIxMiIgcng9IjIiIGZpbGw9IiNDOEEyNEQiIGZpbGwtb3BhY2l0eT0iMC4xNiIvPgogIDwvZz4KICA8ZyBmaWxsPSIjRkZGRkZGIiBmaWxsLW9wYWNpdHk9IjAuMjMiPgogICAgPHJlY3QgeD0iNzgiIHk9IjE1MCIgd2lkdGg9IjciIGhlaWdodD0iOCIgcng9IjEiLz48cmVjdCB4PSI5NCIgeT0iMTUwIiB3aWR0aD0iNyIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9Ijc4IiB5PSIxNzIiIHdpZHRoPSI3IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iOTQiIHk9IjE3MiIgd2lkdGg9IjciIGhlaWdodD0iOCIgcng9IjEiLz4KICAgIDxyZWN0IHg9IjQ0NCIgeT0iMTE0IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjQ2MiIgeT0iMTE0IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjQ0NCIgeT0iMTM4IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjQ2MiIgeT0iMTM4IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPgogICAgPHJlY3QgeD0iNzcyIiB5PSIxMTQiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iNzkyIiB5PSIxMTQiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iNzcyIiB5PSIxNDAiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iNzkyIiB5PSIxNDAiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+CiAgICA8cmVjdCB4PSIxMTU2IiB5PSIxNDIiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iMTE3NiIgeT0iMTQyIiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjExNTYiIHk9IjE2OCIgd2lkdGg9IjgiIGhlaWdodD0iOCIgcng9IjEiLz48cmVjdCB4PSIxMTc2IiB5PSIxNjgiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+CiAgPC9nPgogIDxwYXRoIGQ9Ik0wIDIzNyBIMTQwMCIgc3Ryb2tlPSIjMkU1RjgwIiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPg==");
    background-repeat: no-repeat;
    background-position: center bottom;
    background-size: min(1180px, 92vw) auto;
    mix-blend-mode: multiply;
}
.block-container > div { position: relative; z-index: 3; }

[data-testid="stSidebar"]::after {
    content: "";
    position: absolute;
    left: -12px;
    right: -12px;
    bottom: -6px;
    height: 138px;
    z-index: 0;
    pointer-events: none;
    opacity: .64;
    background-image:
        linear-gradient(to top, rgba(255,255,255,.98) 0%, rgba(255,255,255,.82) 42%, rgba(255,255,255,.20) 78%, rgba(255,255,255,0) 100%),
        url("data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNDAwIDI2MCIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNYXggbWVldCI+CiAgPGRlZnM+CiAgICA8bGluZWFyR3JhZGllbnQgaWQ9InNreSIgeDE9IjAiIHgyPSIxIiB5MT0iMCIgeTI9IjAiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiM1RTdGOTYiIHN0b3Atb3BhY2l0eT0iMC4xNiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjAuMzQiIHN0b3AtY29sb3I9IiMyRTVGODAiIHN0b3Atb3BhY2l0eT0iMC4yMiIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjAuNjQiIHN0b3AtY29sb3I9IiM3REFBOTIiIHN0b3Atb3BhY2l0eT0iMC4xNSIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNDOEEyNEQiIHN0b3Atb3BhY2l0eT0iMC4xMiIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICAgIDxsaW5lYXJHcmFkaWVudCBpZD0iZ29sZCIgeDE9IjAiIHgyPSIwIiB5MT0iMCIgeTI9IjEiPgogICAgICA8c3RvcCBvZmZzZXQ9IjAiIHN0b3AtY29sb3I9IiNDOEEyNEQiIHN0b3Atb3BhY2l0eT0iMC4yOCIvPgogICAgICA8c3RvcCBvZmZzZXQ9IjEiIHN0b3AtY29sb3I9IiNDOEEyNEQiIHN0b3Atb3BhY2l0eT0iMC4wOCIvPgogICAgPC9saW5lYXJHcmFkaWVudD4KICA8L2RlZnM+CiAgPHBhdGggZD0iTTAgMjI5IEMxMTAgMjE2IDIxMCAyMTggMzE1IDIyNCBDNDMwIDIzMCA1MjAgMjEwIDYzMiAyMTggQzc1NiAyMjggODcwIDIxNCA5ODkgMjIwIEMxMTEwIDIyNiAxMjQwIDIxMCAxNDAwIDIyMCBMMTQwMCAyNjAgTDAgMjYwIFoiIGZpbGw9IiNGRkZGRkYiIGZpbGwtb3BhY2l0eT0iMC43MiIvPgogIDxnIGZpbGw9InVybCgjc2t5KSI+CiAgICA8cmVjdCB4PSIxMiIgeT0iMTY0IiB3aWR0aD0iNDIiIGhlaWdodD0iNzIiIHJ4PSIzIi8+CiAgICA8cmVjdCB4PSI2MiIgeT0iMTM0IiB3aWR0aD0iNTgiIGhlaWdodD0iMTAyIiByeD0iNCIvPgogICAgPHJlY3QgeD0iMTMwIiB5PSIxNTQiIHdpZHRoPSI0OCIgaGVpZ2h0PSI4MiIgcng9IjMiLz4KICAgIDxyZWN0IHg9IjE5MCIgeT0iMTEyIiB3aWR0aD0iNzAiIGhlaWdodD0iMTI0IiByeD0iNSIvPgogICAgPHBhdGggZD0iTTI3NiAyMzYgTDI3NiAxMTggTDMxOCAxMTggTDMxOCA5OCBMMzUwIDk4IEwzNTAgMjM2IFoiLz4KICAgIDxyZWN0IHg9IjM2NiIgeT0iMTQ1IiB3aWR0aD0iNDgiIGhlaWdodD0iOTEiIHJ4PSIzIi8+CiAgICA8cmVjdCB4PSI0MjYiIHk9IjkyIiB3aWR0aD0iNzQiIGhlaWdodD0iMTQ0IiByeD0iNSIvPgogICAgPHJlY3QgeD0iNTEyIiB5PSIxMjgiIHdpZHRoPSI1NCIgaGVpZ2h0PSIxMDgiIHJ4PSI0Ii8+CiAgICA8cGF0aCBkPSJNNTg4IDIzNiBMNTg4IDE2NCBMNjI1IDEzMiBMNjYyIDE2NCBMNjYyIDIzNiBaIi8+CiAgICA8cmVjdCB4PSI2NzYiIHk9IjE1MCIgd2lkdGg9IjYwIiBoZWlnaHQ9Ijg2IiByeD0iNCIvPgogICAgPHJlY3QgeD0iNzU0IiB5PSI5MiIgd2lkdGg9IjcyIiBoZWlnaHQ9IjE0NCIgcng9IjUiLz4KICAgIDxyZWN0IHg9Ijg0MCIgeT0iMTI4IiB3aWR0aD0iNDYiIGhlaWdodD0iMTA4IiByeD0iMyIvPgogICAgPHJlY3QgeD0iOTAwIiB5PSIxNTYiIHdpZHRoPSI3OCIgaGVpZ2h0PSI4MCIgcng9IjQiLz4KICAgIDxyZWN0IHg9Ijk5NCIgeT0iMTEwIiB3aWR0aD0iNjAiIGhlaWdodD0iMTI2IiByeD0iNSIvPgogICAgPHJlY3QgeD0iMTA2NiIgeT0iMTQyIiB3aWR0aD0iNTYiIGhlaWdodD0iOTQiIHJ4PSI0Ii8+CiAgICA8cmVjdCB4PSIxMTM2IiB5PSIxMjAiIHdpZHRoPSI3MiIgaGVpZ2h0PSIxMTYiIHJ4PSI1Ii8+CiAgICA8cmVjdCB4PSIxMjIyIiB5PSIxNTYiIHdpZHRoPSI1MiIgaGVpZ2h0PSI4MCIgcng9IjMiLz4KICAgIDxyZWN0IHg9IjEyODgiIHk9IjEzNCIgd2lkdGg9Ijc4IiBoZWlnaHQ9IjEwMiIgcng9IjUiLz4KICA8L2c+CiAgPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNjUwIDApIj4KICAgIDxwYXRoIGQ9Ik00OCAyMzYgTDU2IDEwMSBMNjUgMjM2IFoiIGZpbGw9InVybCgjZ29sZCkiLz4KICAgIDxwYXRoIGQ9Ik02MCA5MiBMNjQgNTQgTDY4IDkyIFoiIGZpbGw9IiNDOEEyNEQiIGZpbGwtb3BhY2l0eT0iMC4yNSIvPgogICAgPGNpcmNsZSBjeD0iNjQiIGN5PSIxMDMiIHI9IjE3IiBmaWxsPSIjQzhBMjREIiBmaWxsLW9wYWNpdHk9IjAuMTMiLz4KICAgIDxyZWN0IHg9IjQ2IiB5PSIyMjQiIHdpZHRoPSIzOCIgaGVpZ2h0PSIxMiIgcng9IjIiIGZpbGw9IiNDOEEyNEQiIGZpbGwtb3BhY2l0eT0iMC4xNiIvPgogIDwvZz4KICA8ZyBmaWxsPSIjRkZGRkZGIiBmaWxsLW9wYWNpdHk9IjAuMjMiPgogICAgPHJlY3QgeD0iNzgiIHk9IjE1MCIgd2lkdGg9IjciIGhlaWdodD0iOCIgcng9IjEiLz48cmVjdCB4PSI5NCIgeT0iMTUwIiB3aWR0aD0iNyIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9Ijc4IiB5PSIxNzIiIHdpZHRoPSI3IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iOTQiIHk9IjE3MiIgd2lkdGg9IjciIGhlaWdodD0iOCIgcng9IjEiLz4KICAgIDxyZWN0IHg9IjQ0NCIgeT0iMTE0IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjQ2MiIgeT0iMTE0IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjQ0NCIgeT0iMTM4IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjQ2MiIgeT0iMTM4IiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPgogICAgPHJlY3QgeD0iNzcyIiB5PSIxMTQiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iNzkyIiB5PSIxMTQiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iNzcyIiB5PSIxNDAiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iNzkyIiB5PSIxNDAiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+CiAgICA8cmVjdCB4PSIxMTU2IiB5PSIxNDIiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+PHJlY3QgeD0iMTE3NiIgeT0iMTQyIiB3aWR0aD0iOCIgaGVpZ2h0PSI4IiByeD0iMSIvPjxyZWN0IHg9IjExNTYiIHk9IjE2OCIgd2lkdGg9IjgiIGhlaWdodD0iOCIgcng9IjEiLz48cmVjdCB4PSIxMTc2IiB5PSIxNjgiIHdpZHRoPSI4IiBoZWlnaHQ9IjgiIHJ4PSIxIi8+CiAgPC9nPgogIDxwYXRoIGQ9Ik0wIDIzNyBIMTQwMCIgc3Ryb2tlPSIjMkU1RjgwIiBzdHJva2Utb3BhY2l0eT0iMC4xNiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPg==");
    background-repeat: no-repeat;
    background-position: center bottom;
    background-size: 360px auto;
    mix-blend-mode: multiply;
}
[data-testid="stSidebar"] > div { position: relative; z-index: 3; }

/* Keep the Jakarta watermark decorative only: hide it on small screens where space is limited. */
@media (max-width: 980px) {
    .block-container::after { display: none; }
}

</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================

DATA_FILES = {
    "clean": "Clean_Dataset_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv",
    "log": "Data_Cleaning_Log_ISPU_Jakarta_Tugas_3_4_5_FINAL.csv",
    "audit": "Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv",
    "validation": "Validasi_Final_Clean_Dataset_ISPU_Jakarta_FINAL.csv",
}

# Data contract utama. Dashboard harus gagal secara jelas bila kolom wajib hilang,
# bukan berhenti diam-diam atau menampilkan visual yang keliru.
DATE_COLUMN_OPTIONS = ["tanggal_clean", "tanggal"]
REQUIRED_COLUMNS = ["stasiun", "max", "categori", "critical"]
RECOMMENDED_COLUMNS = [*POLLUTANT_COLS, "flag_tidak_sehat_plus"]


def validate_required_columns(df: pd.DataFrame) -> None:
    """Validate the minimum schema needed for the executive dashboard."""
    missing_required = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    has_date_column = any(col in df.columns for col in DATE_COLUMN_OPTIONS)

    messages = []
    if not has_date_column:
        messages.append("- Kolom tanggal tidak ditemukan. Harus ada salah satu: `tanggal_clean` atau `tanggal`.")
    if missing_required:
        messages.append("- Kolom wajib hilang: " + ", ".join(f"`{col}`" for col in missing_required) + ".")

    if messages:
        available = ", ".join(df.columns.astype(str).tolist())
        raise ValueError(
            "Schema clean dataset tidak sesuai kontrak dashboard.\n"
            + "\n".join(messages)
            + "\n\nKolom yang tersedia saat ini: "
            + available
        )


def get_schema_notes(df: pd.DataFrame) -> list[str]:
    """Return non-blocking notes for recommended columns that are absent."""
    missing_recommended = [col for col in RECOMMENDED_COLUMNS if col not in df.columns]
    notes = []
    if missing_recommended:
        notes.append(
            "Kolom rekomendasi tidak ditemukan: "
            + ", ".join(f"`{col}`" for col in missing_recommended)
            + ". Beberapa panel diagnostik mungkin lebih terbatas."
        )
    return notes


def find_file(filename: str) -> Optional[Path]:
    """Find a data file in common deployment locations."""
    here = Path(__file__).resolve().parent
    candidates = [
        here / "data" / filename,
        here / filename,
        Path.cwd() / "data" / filename,
        Path.cwd() / filename,
        Path("/mnt/data/Output_Final_Tugas_3_4_5_ISPU_Jakarta") / filename,
        Path("/mnt/data") / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


@st.cache_data(show_spinner=False)
def load_csv_by_key(key: str) -> pd.DataFrame:
    filename = DATA_FILES[key]
    path = find_file(filename)
    if path is None:
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner=True)
def load_all_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clean = load_csv_by_key("clean")
    log = load_csv_by_key("log")
    audit = load_csv_by_key("audit")
    validation = load_csv_by_key("validation")

    if clean.empty:
        return clean, log, audit, validation

    validate_required_columns(clean)
    schema_notes = get_schema_notes(clean)
    clean = prepare_clean_data(clean)
    clean.attrs["schema_notes"] = schema_notes
    if not audit.empty:
        audit = prepare_audit_data(audit)
    return clean, log, audit, validation


def normalize_text_series(series: pd.Series) -> pd.Series:
    return (
        series.astype("string")
        .str.strip()
        .str.upper()
        .replace({"<NA>": np.nan, "NAN": np.nan, "NONE": np.nan, "": np.nan})
    )



def to_bool_value(value) -> bool:
    if pd.isna(value):
        return False
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return bool(value)
    text = str(value).strip().lower()
    if text in {"true", "1", "yes", "y", "ya", "benar"}:
        return True
    if text in {"false", "0", "no", "n", "tidak", "salah", ""}:
        return False
    return bool(value)


def to_bool_series(series: pd.Series) -> pd.Series:
    return series.map(to_bool_value).astype(bool)


def prepare_clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "tanggal_clean" in df.columns:
        df["tanggal_clean"] = pd.to_datetime(df["tanggal_clean"], errors="coerce")
    elif "tanggal" in df.columns:
        df["tanggal_clean"] = pd.to_datetime(df["tanggal"], errors="coerce")
    else:
        raise ValueError("Dataset tidak memiliki kolom tanggal/tanggal_clean.")

    df = df.dropna(subset=["tanggal_clean"]).copy()
    df["tanggal"] = df["tanggal_clean"].dt.date.astype(str)
    df["tahun"] = df.get("tahun", df["tanggal_clean"].dt.year).astype(int)
    df["bulan"] = df.get("bulan", df["tanggal_clean"].dt.month).astype(int)
    df["nama_bulan"] = pd.Categorical(
        df.get("nama_bulan", df["tanggal_clean"].dt.month.map(lambda x: MONTH_ORDER[x - 1])),
        categories=MONTH_ORDER,
        ordered=True,
    )
    df["tahun_bulan"] = df.get("tahun_bulan", df["tanggal_clean"].dt.to_period("M").astype(str)).astype(str)

    if "stasiun" not in df.columns:
        raise ValueError("Dataset tidak memiliki kolom stasiun.")
    df["stasiun"] = df["stasiun"].astype("string").str.strip()

    df["categori"] = normalize_text_series(df.get("categori", pd.Series(index=df.index, dtype="object"))).fillna("TIDAK ADA DATA")
    df["critical"] = normalize_text_series(df.get("critical", pd.Series(index=df.index, dtype="object"))).fillna("TIDAK ADA DATA")

    for col in ["max", *POLLUTANT_COLS]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "flag_tidak_sehat_plus" in df.columns:
        df["flag_tidak_sehat_plus"] = to_bool_series(df["flag_tidak_sehat_plus"])
    else:
        df["flag_tidak_sehat_plus"] = df["categori"].isin(["TIDAK SEHAT", "SANGAT TIDAK SEHAT", "BERBAHAYA"])

    if "used_for_main_dashboard_kpi" in df.columns:
        df["used_for_main_dashboard_kpi"] = to_bool_series(df["used_for_main_dashboard_kpi"])
    else:
        df["used_for_main_dashboard_kpi"] = True

    for bool_col in ["flag_multi_critical", "flag_multi_param_max"]:
        if bool_col in df.columns:
            df[bool_col] = to_bool_series(df[bool_col])

    return df.sort_values("tanggal_clean").reset_index(drop=True)


def prepare_audit_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    date_col = "tanggal" if "tanggal" in df.columns else "tanggal_clean"
    if date_col in df.columns:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    if "categori" in df.columns:
        df["categori"] = normalize_text_series(df["categori"]).fillna("TIDAK ADA DATA")
    if "critical" in df.columns:
        df["critical"] = normalize_text_series(df["critical"]).fillna("TIDAK ADA DATA")
    for bool_col in ["flag_multi_critical", "flag_multi_param_max", "used_for_main_dashboard_kpi"]:
        if bool_col in df.columns:
            df[bool_col] = to_bool_series(df[bool_col])
    return df


# =============================================================================
# UTILITIES
# =============================================================================


def fmt_int(value: float | int | None) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{int(round(float(value))):,}".replace(",", ".")


def fmt_float(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):,.{digits}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_pct(value: float | int | None, digits: int = 1) -> str:
    if value is None or pd.isna(value):
        return "—"
    return f"{float(value):.{digits}f}%".replace(".", ",")


def pct_true(series: pd.Series) -> float:
    if series.empty:
        return np.nan
    return float(series.astype(bool).mean() * 100)


def obs_context(df: pd.DataFrame) -> str:
    """Human-readable denominator used in KPI and insight copy."""
    return f"{fmt_int(len(df))} observasi tanggal-stasiun"


def obs_context_active(df: pd.DataFrame) -> str:
    return f"{obs_context(df)} pada filter aktif"


def mode_or_dash(series: pd.Series) -> str:
    s = series.dropna().astype(str)
    s = s[s.str.upper() != "TIDAK ADA DATA"]
    if s.empty:
        return "—"
    mode = s.mode()
    return str(mode.iloc[0]) if not mode.empty else "—"


def station_code(name: str) -> str:
    if not isinstance(name, str):
        return "—"
    parts = name.split()
    for part in parts:
        if part.upper().startswith("DKI"):
            return part.upper()
    return name[:4].upper()


def risk_level(pct_unhealthy: float | None) -> str:
    if pct_unhealthy is None or pd.isna(pct_unhealthy):
        return "Tidak Ada Data"
    if pct_unhealthy >= 30:
        return "Prioritas Tinggi"
    if pct_unhealthy >= 15:
        return "Prioritas Menengah"
    return "Prioritas Pemantauan"


def ispu_status_from_average(avg: float | None) -> str:
    if avg is None or pd.isna(avg):
        return "Tidak Ada Data"
    if avg <= 50:
        return "BAIK"
    if avg <= 100:
        return "SEDANG"
    if avg <= 200:
        return "TIDAK SEHAT"
    if avg <= 300:
        return "SANGAT TIDAK SEHAT"
    return "BERBAHAYA"


def calc_category_from_ispu(value: float | None) -> str:
    return ispu_status_from_average(value)


def safe_html_text(value, allow_br: bool = False) -> str:
    """Escape dynamic text before inserting it into custom HTML blocks.

    Streamlit renders raw HTML through Markdown. Any user/data-derived text
    must be escaped so station names, categories, or notes never break the
    markup. When a value intentionally uses <br>, allow it explicitly.
    """
    if value is None:
        text = ""
    else:
        text = html_escape(str(value))
    if allow_br:
        text = (
            text.replace("&lt;br&gt;", "<br>")
            .replace("&lt;br/&gt;", "<br>")
            .replace("&lt;br /&gt;", "<br>")
        )
    return text


def kpi_card(label: str, value: str, delta: str = "", note: str = "", accent: str = "#00A676") -> None:
    """Render a KPI card without Markdown code-block leakage.

    The previous multi-line indented HTML caused Streamlit Markdown to treat
    nested fragments such as <div class="kpi-note"> as a code block on some
    deployments. This version builds one compact HTML fragment with escaped
    dynamic values.
    """
    label_html = safe_html_text(label)
    value_html = safe_html_text(value, allow_br=True)
    delta_html = f'<div class="kpi-delta">{safe_html_text(delta, allow_br=True)}</div>' if delta else ""
    note_html = f'<div class="kpi-note">{safe_html_text(note, allow_br=True)}</div>' if note else ""
    accent_html = safe_html_text(accent)
    html = (
        f'<div class="kpi-card" style="--accent:{accent_html};">'
        f'<div class="kpi-label">{label_html}</div>'
        f'<div class="kpi-value">{value_html}</div>'
        f'{delta_html}'
        f'{note_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_title(title: str) -> None:
    title_html = safe_html_text(title)
    st.markdown(
        f'<div class="section-title"><div class="bar"></div><h3>{title_html}</h3></div>',
        unsafe_allow_html=True,
    )




def page_brief(title: str, body: str) -> None:
    """Render one compact decision context line.

    Kept intentionally small so it informs the decision context without pushing
    KPI cards and visuals below the fold.
    """
    title_html = safe_html_text(title)
    body_html = safe_html_text(body, allow_br=True)
    html = (
        f'<div class="page-brief">'
        f'<span class="context-kicker">{title_html}</span>'
        f'<span class="context-body">{body_html}</span>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def air_quality_ribbon(df: pd.DataFrame) -> str:
    if df.empty or "categori" not in df.columns:
        return ""
    counts = category_counts(df)
    total = max(float(counts["jumlah"].sum()), 1.0)
    segments = []
    legends = []
    for _, row in counts.iterrows():
        cat = str(row["categori"])
        pct = float(row["jumlah"]) / total * 100
        color = CATEGORY_COLORS.get(cat, "#64748B")
        width = max(pct, 1.2) if row["jumlah"] > 0 else 0
        cat_html = safe_html_text(cat)
        color_html = safe_html_text(color)
        if width > 0:
            segments.append(
                f'<div class="air-ribbon-segment" title="{cat_html}: {pct:.1f}%" '
                f'style="width:{width:.3f}%; background:{color_html};"></div>'
            )
        legends.append(f'<span class="legend-dot" style="--dot:{color_html};">{cat_html}: {pct:.1f}%</span>')
    return (
        '<div class="air-ribbon-wrap">'
        '<div class="air-ribbon-title"><span>Spektrum kategori ISPU pada filter aktif</span><span>Baik → Berbahaya</span></div>'
        f'<div class="air-ribbon">{"".join(segments)}</div>'
        f'<div class="air-ribbon-legend">{"".join(legends)}</div>'
        '</div>'
    )


def insight_panel(title: str, body: str, kind: str = "insight") -> None:
    class_name = "warning-panel" if kind == "warning" else "insight-panel"
    # Body may intentionally include simple <b> tags generated by the app for emphasis.
    title_html = safe_html_text(title)
    if kind == "warning":
        html = f'<div class="{class_name}"><p>{body}</p></div>'
    else:
        html = (
            f'<div class="{class_name}">'
            f'<div class="insight-title">{title_html}</div>'
            f'<p>{body}</p>'
            f'</div>'
        )
    st.markdown(html, unsafe_allow_html=True)


def apply_fig_style(fig: go.Figure, height: Optional[int] = None, legend: bool = True) -> go.Figure:
    """Apply a safe executive chart style.

    The dashboard is shown inside rounded cards. When Plotly keeps the legend
    above the plotting area, long chart titles such as "Komposisi kategori ..."
    can collide with legend titles/items. To avoid text overlap in screenshots
    and Streamlit Cloud, every legend is moved below the plotting area, the
    legend title is removed, and chart margins are expanded deliberately.
    """
    title_text = fig.layout.title.text or ""
    base_height = height or 430
    bottom_margin = 118 if legend else 58
    top_margin = 78
    final_height = base_height + (58 if legend else 0)

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Arial, sans-serif", color="#102033", size=12),
        title=dict(
            text=title_text,
            x=0,
            xanchor="left",
            y=0.985,
            yanchor="top",
            font=dict(family="Barlow Condensed, Inter, sans-serif", color="#102033", size=21),
        ),
        title_font=dict(family="Barlow Condensed, Inter, sans-serif", color="#102033", size=21),
        margin=dict(t=top_margin, r=26, b=bottom_margin, l=42),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="rgba(15,23,42,.22)", font_color="#102033"),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.24,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#1E3448", size=12),
            title=dict(text="", font=dict(color="#102033", size=1)),
            bordercolor="rgba(15,23,42,0)",
            traceorder="normal",
        ) if legend else dict(visible=False),
        legend_title_text="",
        height=final_height,
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor="rgba(15,23,42,.20)",
        tickfont=dict(color="#334155"),
        title_font=dict(color="#334155"),
        automargin=True,
    )
    fig.update_yaxes(
        gridcolor="rgba(15,23,42,.10)",
        zerolinecolor="rgba(15,23,42,.14)",
        tickfont=dict(color="#334155"),
        title_font=dict(color="#334155"),
        automargin=True,
    )
    # Keep continuous colorbars readable on light cards. This is especially
    # important for heatmaps where Plotly's default colorbar title/ticks can be
    # rendered too pale against a white dashboard card.
    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(font=dict(color="#102033", size=13, family="Inter, Arial, sans-serif"), side="right"),
            tickfont=dict(color="#102033", size=12, family="Inter, Arial, sans-serif"),
            bgcolor="rgba(255,255,255,0.98)",
            outlinecolor="rgba(15,23,42,0.25)",
            outlinewidth=1,
            thickness=18,
            len=0.74,
            xpad=10,
            ypad=8,
        )
    )
    # Remove auto legend titles generated by Plotly Express (e.g. "Kategori" or
    # "Status risiko") so they never overlap with the chart title.
    fig.update_layout(legend_title_text="")
    return fig


def add_stacked_percent_labels(fig: go.Figure) -> go.Figure:
    """Show percentage values on stacked bar charts.

    Labels are rendered inside each stack segment so Kepala Dinas can read the
    magnitude without hovering. Yellow/light segments use dark text; darker
    risk colors use white text for contrast.
    """
    dark_text_traces = {"SEDANG", "SO2"}
    for trace in fig.data:
        trace_name = str(getattr(trace, "name", "")).strip().upper()
        y_values = getattr(trace, "y", [])
        labels = []
        for value in y_values:
            try:
                number = float(value)
            except (TypeError, ValueError):
                labels.append("")
                continue
            if pd.isna(number) or number <= 0:
                labels.append("")
            else:
                labels.append(f"{number:.1f}%")
        text_color = "#102033" if trace_name in dark_text_traces else "#FFFFFF"
        trace.update(
            text=labels,
            texttemplate="%{text}",
            textposition="inside",
            insidetextanchor="middle",
            textfont=dict(
                color=text_color,
                size=10,
                family="JetBrains Mono, Inter, Arial, sans-serif",
            ),
            cliponaxis=False,
        )
    fig.update_layout(uniformtext_minsize=8, uniformtext_mode="show")
    return fig


def add_threshold_lines(fig: go.Figure, include_all: bool = False) -> go.Figure:
    thresholds = [(101, "Ambang Tidak Sehat 101", "#EA580C")]
    if include_all:
        thresholds.extend([(201, "Sangat Tidak Sehat 201", "#E11D48"), (301, "Berbahaya 301", "#7C3AED")])
    for y, label, color in thresholds:
        fig.add_hline(
            y=y,
            line_dash="dash",
            line_width=1.5,
            line_color=color,
            annotation_text=label,
            annotation_position="top left",
            annotation_font_color=color,
            annotation_font_size=11,
        )
    return fig


def category_counts(df: pd.DataFrame, by: Optional[list[str]] = None, pct: bool = False) -> pd.DataFrame:
    if by is None:
        out = df.groupby("categori", observed=False).size().reset_index(name="jumlah")
        all_cats = pd.DataFrame({"categori": CATEGORY_ORDER})
        out = all_cats.merge(out, on="categori", how="left").fillna({"jumlah": 0})
        out["jumlah"] = out["jumlah"].astype(int)
        out["persentase"] = out["jumlah"] / max(out["jumlah"].sum(), 1) * 100
        return out
    out = df.groupby(by + ["categori"], observed=False).size().reset_index(name="jumlah")
    if pct:
        total = out.groupby(by)["jumlah"].transform("sum")
        out["persentase"] = out["jumlah"] / total.replace(0, np.nan) * 100
    return out


def station_summary(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=[
                "stasiun", "kode", "observasi", "rata_rata_ispu", "median_ispu", "persen_tidak_sehat_plus",
                "kategori_dominan", "pencemar_dominan", "status_risiko"
            ]
        )
    summary = (
        df.groupby("stasiun", dropna=False)
        .agg(
            observasi=("stasiun", "size"),
            rata_rata_ispu=("max", "mean"),
            median_ispu=("max", "median"),
            persen_tidak_sehat_plus=("flag_tidak_sehat_plus", lambda s: pct_true(s)),
            kategori_dominan=("categori", mode_or_dash),
            pencemar_dominan=("critical", mode_or_dash),
            tanggal_awal=("tanggal_clean", "min"),
            tanggal_akhir=("tanggal_clean", "max"),
        )
        .reset_index()
    )
    summary["kode"] = summary["stasiun"].map(station_code)
    summary["status_risiko"] = summary["persen_tidak_sehat_plus"].map(risk_level)
    summary = summary.sort_values(["persen_tidak_sehat_plus", "rata_rata_ispu"], ascending=False)
    return summary


def latest_year(df: pd.DataFrame) -> Optional[int]:
    if df.empty:
        return None
    return int(df["tahun"].max())


def previous_year_value(df: pd.DataFrame, year: int, value_col: str, agg: str = "mean") -> tuple[float, float, float]:
    current = df[df["tahun"] == year]
    previous = df[df["tahun"] == year - 1]
    if agg == "mean":
        cur = current[value_col].mean()
        prev = previous[value_col].mean()
    elif agg == "pct_true":
        cur = pct_true(current[value_col])
        prev = pct_true(previous[value_col])
    else:
        cur = np.nan
        prev = np.nan
    delta = cur - prev if not pd.isna(cur) and not pd.isna(prev) else np.nan
    return cur, prev, delta



def join_ranked_items(items: list[str]) -> str:
    """Join ranked items for executive copy."""
    cleaned = [str(item) for item in items if item and str(item) != "—"]
    if not cleaned:
        return "—"
    if len(cleaned) == 1:
        return cleaned[0]
    if len(cleaned) == 2:
        return " dan ".join(cleaned)
    return ", ".join(cleaned[:-1]) + ", dan " + cleaned[-1]


def top_station_rank_text(summary: pd.DataFrame, n: int = 3) -> str:
    if summary is None or summary.empty:
        return "—"
    rows = summary.head(n)
    return join_ranked_items([
        f"{station_code(row['stasiun'])} ({fmt_pct(row['persen_tidak_sehat_plus'], 1)})"
        for _, row in rows.iterrows()
    ])


def top_month_rank_text(monthly: pd.DataFrame, metric_col: str = "persen_tidak_sehat_plus", n: int = 3) -> str:
    if monthly is None or monthly.empty or metric_col not in monthly.columns:
        return "—"
    rows = monthly.sort_values(metric_col, ascending=False).head(n)
    if metric_col.startswith("persen"):
        return join_ranked_items([f"{row['nama_bulan']} ({fmt_pct(row[metric_col], 1)})" for _, row in rows.iterrows()])
    return join_ranked_items([f"{row['nama_bulan']} ({fmt_float(row[metric_col], 1)})" for _, row in rows.iterrows()])


def top_critical_rank_text(df: pd.DataFrame, n: int = 3) -> str:
    if df is None or df.empty or "critical" not in df.columns:
        return "—"
    counts = (
        df[df["critical"].notna() & (df["critical"] != "TIDAK ADA DATA")]
        .groupby("critical")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=False)
    )
    if counts.empty:
        return "—"
    total = max(counts["jumlah"].sum(), 1)
    return join_ranked_items([
        f"{row['critical']} ({fmt_pct(row['jumlah'] / total * 100, 1)})"
        for _, row in counts.head(n).iterrows()
    ])


def response_action_by_risk(pct_unhealthy: float | None) -> tuple[str, str]:
    """Return executive response level and operational action for a risk percentage."""
    level = risk_level(pct_unhealthy)
    if level == "Prioritas Tinggi":
        action = "tetapkan sebagai prioritas pengawasan intensif, lakukan validasi lapangan, evaluasi sumber emisi sekitar titik prioritas, dan siapkan komunikasi risiko."
    elif level == "Prioritas Menengah":
        action = "perkuat pemantauan berkala, cek kenaikan tren, dan siapkan respons cepat bila proporsi Tidak Sehat+ meningkat."
    elif level == "Prioritas Pemantauan":
        action = "lanjutkan pemantauan rutin, gunakan sebagai baseline pembanding, dan tetap dalami pencemar dominan bila terjadi lonjakan."
    else:
        action = "data belum cukup untuk menetapkan respons operasional; longgarkan filter atau cek ketersediaan data."
    return level, action


def trend_context_text(current: float, previous: float, historical: float) -> str:
    if pd.isna(current):
        return "belum dapat dinilai karena data tahun terakhir kosong."
    parts = []
    if not pd.isna(previous):
        delta = current - previous
        direction = "lebih tinggi" if delta > 0 else "lebih rendah" if delta < 0 else "sama"
        parts.append(f"{direction} {fmt_pct(abs(delta), 1)} poin dibanding tahun sebelumnya")
    if not pd.isna(historical):
        diff = current - historical
        pos = "di atas" if diff > 0 else "di bawah" if diff < 0 else "setara dengan"
        parts.append(f"{pos} rata-rata historis ({fmt_pct(historical, 1)})")
    return " dan ".join(parts) + "." if parts else "belum dapat dibandingkan dengan periode lain."


def pollutant_policy_guidance(pollutant: str) -> str:
    key = str(pollutant).upper().replace(".", "")
    if key in {"PM25", "PM10"}:
        return "arah awal kebijakan dapat difokuskan pada pengendalian partikulat: transportasi, debu jalan, konstruksi, pembakaran terbuka, serta validasi lapangan di sekitar titik prioritas."
    if key == "NO2":
        return "arah awal kebijakan dapat difokuskan pada sumber pembakaran kendaraan dan lalu lintas, serta evaluasi emisi pada koridor aktivitas tinggi."
    if key == "SO2":
        return "arah awal kebijakan dapat difokuskan pada potensi sumber pembakaran berbasis sulfur/industri/energi dan perlu dikonfirmasi dengan data sumber emisi."
    if key == "CO":
        return "arah awal kebijakan dapat difokuskan pada pembakaran tidak sempurna, aktivitas kendaraan, dan sumber pembakaran lokal."
    if key == "O3":
        return "arah awal kebijakan perlu mempertimbangkan prekursor ozon dan faktor meteorologi karena O3 merupakan polutan sekunder."
    return "arah kebijakan perlu dikonfirmasi dengan data sumber emisi dan validasi lapangan karena parameter dominan belum terklasifikasi jelas."


def decision_grade_body(temuan: str, makna: str, tindakan: str, batasan: str) -> str:
    """Structured executive insight format: finding, meaning, action, caveat."""
    return (
        f"<b>Temuan:</b> {temuan}<br>"
        f"<b>Makna:</b> {makna}<br>"
        f"<b>Arahan tindakan:</b> {tindakan}<br>"
        f"<b>Batasan:</b> {batasan}"
    )


def decision_confidence_text(status: str, validation_issues: int, final_dup: int, total_filtered: int) -> str:
    if status == "Layak digunakan" and total_filtered > 0:
        return "Aman untuk analisis strategis dan evaluatif berbasis data historis: pola risiko, prioritas stasiun, pencemar dominan, periode rawan, dan audit kualitas data."
    if total_filtered == 0:
        return "Tidak cukup data pada filter aktif. Keputusan tidak boleh diambil dari basis data kosong; longgarkan filter terlebih dahulu."
    if final_dup > 0 or validation_issues > 0:
        return "Perlu kehati-hatian. Terdapat isu validasi/duplikasi final yang perlu ditinjau sebelum angka dipakai sebagai dasar keputusan."
    return "Perlu kehati-hatian karena terdapat batasan data yang perlu dibaca bersama catatan metodologi."


def first_available_year(df: pd.DataFrame, parameter_col: str) -> Optional[int]:
    """Return first year where a pollutant parameter is available."""
    if df is None or df.empty or parameter_col not in df.columns or "tahun" not in df.columns:
        return None
    available = df[df[parameter_col].notna()]
    if available.empty:
        return None
    return int(available["tahun"].min())


def parameter_availability_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build parameter availability summary for data confidence and fair comparison."""
    rows = []
    if df is None or df.empty:
        return pd.DataFrame(columns=["Parameter", "Tahun Mulai", "Tahun Akhir", "Coverage", "Tahun Tersedia", "Status", "Catatan Interpretasi"])
    total_rows = max(len(df), 1)
    total_years = max(df["tahun"].nunique(), 1) if "tahun" in df.columns else 1
    for col in POLLUTANT_COLS:
        if col not in df.columns:
            rows.append({
                "Parameter": col.upper(),
                "Tahun Mulai": "—",
                "Tahun Akhir": "—",
                "Coverage": 0.0,
                "Tahun Tersedia": 0,
                "Status": "Tidak tersedia",
                "Catatan Interpretasi": "Parameter tidak tersedia pada dataset final.",
            })
            continue
        available = df[df[col].notna()]
        coverage = float(df[col].notna().mean() * 100)
        if available.empty:
            first_year = last_year = "—"
            years_available = 0
        else:
            first_year = int(available["tahun"].min())
            last_year = int(available["tahun"].max())
            years_available = int(available["tahun"].nunique())
        if coverage >= 95 and years_available >= total_years * 0.95:
            status = "Tersedia kuat"
            note = "Relatif aman untuk pembandingan lintas periode pada filter aktif."
        elif coverage > 0:
            status = "Tersedia parsial"
            note = "Pembandingan lintas periode perlu menggunakan coverage dan persentase, bukan jumlah mentah."
        else:
            status = "Tidak tersedia"
            note = "Tidak dapat digunakan untuk analisis parameter pada filter aktif."
        if col == "pm25" and coverage > 0:
            note = "PM2.5 tersedia mulai periode tertentu; interpretasi historis sebelum tahun mulai tidak boleh dianggap sebagai PM2.5 rendah."
        rows.append({
            "Parameter": col.upper(),
            "Tahun Mulai": first_year,
            "Tahun Akhir": last_year,
            "Coverage": coverage,
            "Tahun Tersedia": years_available,
            "Status": status,
            "Catatan Interpretasi": note,
        })
    return pd.DataFrame(rows)


def parameter_availability_yearly(df: pd.DataFrame) -> pd.DataFrame:
    """Coverage percentage per year and parameter for heatmap."""
    rows = []
    if df is None or df.empty or "tahun" not in df.columns:
        return pd.DataFrame(columns=["tahun", "parameter", "coverage_pct"])
    for year, group in df.groupby("tahun"):
        for col in POLLUTANT_COLS:
            if col in group.columns:
                coverage = float(group[col].notna().mean() * 100)
            else:
                coverage = 0.0
            rows.append({"tahun": int(year), "parameter": col.upper(), "coverage_pct": coverage})
    return pd.DataFrame(rows)


def fig_parameter_availability_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap tahun × parameter untuk melihat fairness pembandingan polutan."""
    coverage = parameter_availability_yearly(df)
    if coverage.empty:
        fig = go.Figure()
        fig.update_layout(title="Ketersediaan parameter per tahun")
        return apply_fig_style(fig, height=420, legend=False)
    pivot = coverage.pivot_table(index="parameter", columns="tahun", values="coverage_pct", fill_value=0)
    pivot = pivot.reindex(index=[c.upper() for c in POLLUTANT_COLS if c.upper() in pivot.index])
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=["#F8FAFC", "#DBEAFE", "#BAE6FD", "#6EE7B7", "#00A676"],
        zmin=0,
        zmax=100,
        title="Heatmap ketersediaan parameter per tahun",
        labels=dict(x="Tahun", y="Parameter", color="Coverage (%)"),
    )
    fig.update_traces(
        text=np.round(pivot.values, 0).astype(int),
        texttemplate="%{text}%",
        textfont=dict(color="#102033", size=11, family="JetBrains Mono, Inter, Arial, sans-serif"),
        hovertemplate="Parameter: %{y}<br>Tahun: %{x}<br>Coverage: %{z:.1f}%<extra></extra>",
    )
    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text="Coverage (%)", font=dict(color="#102033", size=13), side="right"),
            tickfont=dict(color="#102033", size=12),
            bgcolor="rgba(255,255,255,0.98)",
            outlinecolor="rgba(15,23,42,0.28)",
            outlinewidth=1,
            thickness=18,
            len=0.72,
        )
    )
    return apply_fig_style(fig, height=440, legend=False)


def add_context_annotations(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    """Add contextual annotations to time series without claiming causality."""
    if df is None or df.empty or "tanggal_clean" not in df.columns:
        return fig
    date_min = pd.to_datetime(df["tanggal_clean"].min())
    date_max = pd.to_datetime(df["tanggal_clean"].max())

    # COVID-19 contextual period. This is not a causal claim.
    covid_start = CONTEXT_EVENTS["covid_start"]
    covid_end = CONTEXT_EVENTS["covid_end"]
    if date_min <= covid_end and date_max >= covid_start:
        fig.add_vrect(
            x0=max(covid_start, date_min),
            x1=min(covid_end, date_max),
            fillcolor="#64748B",
            opacity=0.10,
            line_width=0,
            annotation_text="COVID-19 (konteks)",
            annotation_position="top left",
            annotation_font_color="#334155",
            annotation_font_size=11,
        )

    # Dynamic PM2.5 availability annotation.
    pm25_year = first_available_year(df, "pm25")
    if pm25_year is not None:
        x_pm25 = pd.Timestamp(year=pm25_year, month=1, day=1)
        if date_min <= x_pm25 <= date_max:
            fig.add_vline(
                x=x_pm25,
                line_dash="dot",
                line_width=1.5,
                line_color="#16A34A",
                annotation_text=f"PM2.5 mulai tersedia ({pm25_year})",
                annotation_position="top right",
                annotation_font_color="#166534",
                annotation_font_size=11,
            )
    return fig


def comparison_guardrail_table() -> pd.DataFrame:
    """Static executive guardrails so comparisons are not over-claimed."""
    return pd.DataFrame([
        {
            "Kondisi": "PM2.5 tersedia mulai periode tertentu",
            "Risiko Salah Tafsir": "PM2.5 terlihat tidak dominan pada tahun awal",
            "Cara Baca yang Benar": "Bandingkan PM2.5 hanya pada periode ketika datanya tersedia atau tampilkan catatan coverage.",
        },
        {
            "Kondisi": "Periode COVID-19 / pembatasan aktivitas",
            "Risiko Salah Tafsir": "Perubahan tren dianggap pasti akibat COVID-19",
            "Cara Baca yang Benar": "Gunakan sebagai anotasi konteks; klaim sebab-akibat membutuhkan analisis kausal dan data aktivitas.",
        },
        {
            "Kondisi": "Jumlah observasi antar stasiun/tahun berbeda",
            "Risiko Salah Tafsir": "Ranking berbasis jumlah mentah menjadi bias",
            "Cara Baca yang Benar": "Gunakan persentase observasi, median, dan coverage sebagai pembanding.",
        },
        {
            "Kondisi": "Critical menunjukkan parameter indeks tertinggi",
            "Risiko Salah Tafsir": "Critical dianggap sebagai konsentrasi fisik terbesar atau penyebab tunggal",
            "Cara Baca yang Benar": "Baca sebagai indikator diagnostik dan validasi dengan data sumber emisi/meteorologi.",
        },
        {
            "Kondisi": "Dashboard menggunakan data historis",
            "Risiko Salah Tafsir": "Dashboard dianggap menunjukkan status udara hari ini",
            "Cara Baca yang Benar": "Gunakan untuk pola dan prioritas; keputusan real-time memerlukan data pemantauan terbaru.",
        },
    ])


# =============================================================================
# LIGHT TABLE RENDERER
# =============================================================================


def _chip_palette(value: object) -> tuple[str, str, str, str]:
    text = str(value).strip()
    upper = text.upper()
    category_bg = {
        "BAIK": ("#E6FFF4", "#78D6B0", "#064E3B", CATEGORY_COLORS["BAIK"]),
        "SEDANG": ("#FFF7D6", "#F6D365", "#4A3411", CATEGORY_COLORS["SEDANG"]),
        "TIDAK SEHAT": ("#FFF1E8", "#FDBA74", "#7C2D12", CATEGORY_COLORS["TIDAK SEHAT"]),
        "SANGAT TIDAK SEHAT": ("#FFF1F3", "#FDA4AF", "#881337", CATEGORY_COLORS["SANGAT TIDAK SEHAT"]),
        "BERBAHAYA": ("#F3EEFF", "#C4B5FD", "#3B0764", CATEGORY_COLORS["BERBAHAYA"]),
    }
    if upper in category_bg:
        return category_bg[upper]
    if text in RISK_COLORS or upper in {"PRIORITAS TINGGI", "PRIORITAS MENENGAH", "PRIORITAS PEMANTAUAN"}:
        if "TINGGI" in upper:
            return ("#FFF1F3", "#FDA4AF", "#881337", "#E11D48")
        if "MENENGAH" in upper:
            return ("#FFF7D6", "#F6D365", "#4A3411", "#F97316")
        return ("#E6FFF4", "#78D6B0", "#064E3B", "#00A676")
    if upper in {"AMAN", "VALID", "LAYAK DIGUNAKAN", "TRUE", "YA"}:
        return ("#E6FFF4", "#78D6B0", "#064E3B", "#00A676")
    if upper in {"PERLU PERHATIAN", "FALSE", "TIDAK"} or "REVIEW" in upper:
        return ("#FFF7D6", "#F6D365", "#4A3411", "#F4B400")
    if upper in CRITICAL_COLORS:
        return ("#F8FAFC", "#CBD5E1", "#102033", CRITICAL_COLORS[upper])
    return ("#F8FAFC", "#CBD5E1", "#102033", "#64748B")


def _risk_bar_color(value: float) -> str:
    if pd.isna(value):
        return "#64748B"
    if value >= 30:
        return "#E11D48"
    if value >= 15:
        return "#F97316"
    return "#00A676"


def _format_table_value(value: object, col: str, numeric_cols: set[str], int_cols: set[str]) -> str:
    if value is None or pd.isna(value):
        return "—"
    if col in int_cols:
        return fmt_int(value)
    if col in numeric_cols:
        return fmt_float(value, 1)
    if isinstance(value, (float, np.floating)):
        return fmt_float(value, 1)
    if isinstance(value, (int, np.integer)):
        return fmt_int(value)
    if isinstance(value, (bool, np.bool_)):
        return "Ya" if bool(value) else "Tidak"
    return str(value)


def render_light_table(
    df: pd.DataFrame,
    *,
    progress_cols: Optional[list[str]] = None,
    numeric_cols: Optional[list[str]] = None,
    int_cols: Optional[list[str]] = None,
    chip_cols: Optional[list[str]] = None,
    long_cols: Optional[list[str]] = None,
    max_height: int = 520,
    max_rows: Optional[int] = None,
) -> None:
    """Render a readable light-theme HTML table.

    This avoids Streamlit's dataframe renderer, which can appear dark depending
    on the viewer theme. The table is intentionally static but clearer for
    executive review and screenshots.
    """
    if df is None or df.empty:
        st.info("Tidak ada data untuk ditampilkan pada tabel ini.")
        return

    progress_cols = set(progress_cols or [])
    numeric_cols = set(numeric_cols or [])
    int_cols = set(int_cols or [])
    chip_cols = set(chip_cols or [])
    long_cols = set(long_cols or [])

    table_df = df.copy()
    original_len = len(table_df)
    if max_rows is not None and len(table_df) > max_rows:
        table_df = table_df.head(max_rows)

    header = "".join(f"<th>{html_escape(str(col))}</th>" for col in table_df.columns)
    rows_html: list[str] = []
    for _, row in table_df.iterrows():
        cells: list[str] = []
        for col in table_df.columns:
            value = row[col]
            classes = ["long-cell" if col in long_cols else "nowrap-cell"]
            if col in numeric_cols or col in int_cols:
                classes.append("num-cell")

            if col in progress_cols:
                try:
                    pct_value = float(value)
                except Exception:
                    pct_value = np.nan
                width = 0 if pd.isna(pct_value) else max(0, min(100, pct_value))
                bar = _risk_bar_color(pct_value)
                rendered = (
                    f'<div class="light-progress"><div class="light-progress-track">'
                    f'<div class="light-progress-fill" style="width:{width:.2f}%; --bar:{bar};"></div>'
                    f'</div><span class="light-progress-value">{html_escape(fmt_pct(pct_value, 1))}</span></div>'
                )
            elif col in chip_cols:
                text = _format_table_value(value, col, numeric_cols, int_cols)
                bg, border, ink, dot = _chip_palette(text)
                rendered = f'<span class="table-chip" style="--chip-bg:{bg}; --chip-border:{border}; --chip-ink:{ink}; --chip-dot:{dot};">{html_escape(text)}</span>'
            else:
                rendered = html_escape(_format_table_value(value, col, numeric_cols, int_cols))
            cells.append(f'<td class="{" ".join(classes)}">{rendered}</td>')
        rows_html.append(f'<tr>{"".join(cells)}</tr>')

    html = (
        f'<div class="light-table-wrap" style="max-height:{max_height}px;">'
        f'<table class="light-table"><thead><tr>{header}</tr></thead><tbody>{"".join(rows_html)}</tbody></table>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if max_rows is not None and original_len > max_rows:
        st.markdown(f'<div class="table-note">Menampilkan {fmt_int(max_rows)} dari {fmt_int(original_len)} baris. Gunakan tombol unduh untuk melihat data lengkap.</div>', unsafe_allow_html=True)

def download_filtered_data(df: pd.DataFrame, filename: str) -> None:
    st.download_button(
        label="Unduh data terfilter",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def hero(current_page: str, df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    """Render compact header safely.

    The previous implementation placed the full hero, decision cards, and the
    Air Quality Ribbon inside one large nested Markdown/HTML block. In some
    Streamlit/Markdown renderers, the final closing tag can be interpreted as
    literal text and shown as `</div>`. This version renders each HTML block as
    a complete, self-contained fragment to prevent orphan closing tags.
    """
    if df.empty:
        period = "Data belum tersedia"
        status = "Perlu unggah data"
        active_observations = "0"
    else:
        status = "Clean dataset final"
        if filtered.empty:
            period = "Tidak ada data pada filter aktif"
            active_observations = "0"
        else:
            # Periode pada kartu mengikuti data yang benar-benar aktif setelah filter sidebar
            # diterapkan, sehingga pimpinan tidak membaca periode global secara keliru.
            start = filtered["tanggal_clean"].min().strftime("%d %b %Y")
            end = filtered["tanggal_clean"].max().strftime("%d %b %Y")
            period = f"{start} – {end}"
            active_observations = fmt_int(len(filtered))

    hero_html = f"""
    <div class="command-hero" aria-label="Observatorium kualitas udara Jakarta dengan nuansa langit terang dan spektrum risiko ISPU">
        <div class="hero-grid">
            <div>
                <div class="hero-eyebrow">Kualitas Udara DKI Jakarta · {html_escape(str(current_page))}</div>
                <h1 class="hero-title">{html_escape(APP_TITLE)}</h1>
                <div class="hero-copy">{html_escape(APP_SUBTITLE)}</div>
            </div>
            <div class="hero-meta">
                <div class="label">Periode data aktif</div>
                <div class="value">{html_escape(period)}</div>
                <div class="badge-line">
                    <div class="status">{html_escape(status)}</div>
                    <div class="obs-badge">{html_escape(active_observations)} observasi aktif</div>
                    <div class="data-badge">Data historis · bukan status udara real-time</div>
                </div>
            </div>
        </div>
    </div>
    """
    st.markdown(dedent(hero_html).strip(), unsafe_allow_html=True)

    # Decision KPI cards intentionally are not rendered in hero to avoid redundancy.
    # The single source of executive KPIs is the page-level KPI section.
    ribbon_html = air_quality_ribbon(filtered)
    if ribbon_html:
        st.markdown(dedent(ribbon_html).strip(), unsafe_allow_html=True)



def empty_state() -> None:
    st.markdown(
        '<div class="empty-state-panel"><b>Tidak ada data pada filter aktif.</b><br>'
        'Longgarkan rentang periode, pilih kembali stasiun, kategori, atau pencemar kritis. '
        'Dashboard tidak merender grafik kosong agar keputusan tidak dibaca dari basis data nol.</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# FILTERS
# =============================================================================


def build_sidebar(df: pd.DataFrame) -> tuple[str, pd.DataFrame, dict]:
    with st.sidebar:
        st.markdown("### Panel Pemantauan Udara")
        page = st.radio("Pilih dashboard", MENU_ITEMS, index=0)
        st.markdown(f'<div class="sidebar-purpose">{PAGE_PURPOSE.get(page, "")}</div>', unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Filter eksekutif")

        if df.empty:
            st.warning("Clean dataset belum terbaca.")
            return page, df, {}

        min_date = df["tanggal_clean"].min().date()
        max_date = df["tanggal_clean"].max().date()
        year_max = int(df["tahun"].max())

        period_mode = st.radio(
            "Fokus periode",
            ["Tahun terakhir tersedia", "Seluruh periode", "Rentang khusus"],
            index=0,
            help="Default memakai tahun terakhir karena keputusan pimpinan membutuhkan kondisi paling terkini.",
        )

        if period_mode == "Tahun terakhir tersedia":
            start_date = pd.Timestamp(year=year_max, month=1, day=1).date()
            end_date = max_date
        elif period_mode == "Seluruh periode":
            start_date = min_date
            end_date = max_date
        else:
            date_range = st.date_input(
                "Rentang tanggal",
                value=(max(pd.Timestamp(year=year_max, month=1, day=1).date(), min_date), max_date),
                min_value=min_date,
                max_value=max_date,
            )
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
            else:
                start_date, end_date = min_date, max_date

        station_options = sorted(df["stasiun"].dropna().unique().tolist())
        selected_stations = st.multiselect(
            "Stasiun pemantau",
            options=station_options,
            default=station_options,
            format_func=lambda x: f"{station_code(x)} · {x.replace(station_code(x), '').strip()}" if station_code(x) in x else x,
        )

        cat_options = [c for c in CATEGORY_ORDER if c in df["categori"].unique()] + [
            c for c in sorted(df["categori"].dropna().unique()) if c not in CATEGORY_ORDER
        ]
        selected_categories = st.multiselect("Kategori ISPU", options=cat_options, default=cat_options)

        critical_options = [c for c in ["PM10", "PM25", "SO2", "CO", "O3", "NO2"] if c in df["critical"].unique()] + [
            c for c in sorted(df["critical"].dropna().unique()) if c not in ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]
        ]
        selected_critical = st.multiselect("Pencemar kritis", options=critical_options, default=critical_options)

        st.markdown("---")
        st.caption(
            "KPI utama dihitung dari clean dataset final pada unit observasi tanggal-stasiun. Data audit ditampilkan terpisah agar keputusan tidak terdistorsi oleh duplikasi atau baris yang dipisahkan."
        )

    mask = (
        (df["tanggal_clean"].dt.date >= start_date)
        & (df["tanggal_clean"].dt.date <= end_date)
        & (df["stasiun"].isin(selected_stations))
        & (df["categori"].isin(selected_categories))
        & (df["critical"].isin(selected_critical))
    )
    filtered = df.loc[mask].copy()

    filters = {
        "period_mode": period_mode,
        "start_date": start_date,
        "end_date": end_date,
        "selected_stations": selected_stations,
        "selected_categories": selected_categories,
        "selected_critical": selected_critical,
    }
    return page, filtered, filters


# =============================================================================
# VISUAL COMPONENTS
# =============================================================================


def fig_category_distribution(df: pd.DataFrame, title: str = "Distribusi kategori ISPU") -> go.Figure:
    dist = category_counts(df)
    fig = px.bar(
        dist,
        x="categori",
        y="persentase",
        color="categori",
        color_discrete_map=CATEGORY_COLORS,
        text=dist["persentase"].round(1),
        category_orders={"categori": CATEGORY_ORDER},
        title=title,
        labels={"categori": "Kategori", "persentase": "Persentase observasi (%)"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_yaxes(range=[0, max(10, dist["persentase"].max() * 1.25)])
    return apply_fig_style(fig, height=410, legend=False)


def fig_critical_distribution(df: pd.DataFrame, title: str = "Pencemar kritis dominan") -> go.Figure:
    crit = (
        df[df["critical"].notna()]
        .groupby("critical")
        .size()
        .reset_index(name="jumlah")
        .sort_values("jumlah", ascending=True)
    )
    if crit.empty:
        crit = pd.DataFrame({"critical": ["Tidak ada data"], "jumlah": [0]})
    total = max(crit["jumlah"].sum(), 1)
    crit["persentase"] = crit["jumlah"] / total * 100
    crit["label"] = crit["persentase"].map(lambda x: f"{x:.1f}%")
    fig = px.bar(
        crit,
        y="critical",
        x="jumlah",
        orientation="h",
        color="critical",
        color_discrete_map=CRITICAL_COLORS,
        text="label",
        title=title,
        labels={"critical": "Pencemar", "jumlah": "Jumlah observasi"},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(range=[0, max(1, crit["jumlah"].max() * 1.18)])
    return apply_fig_style(fig, height=410, legend=False)


def fig_unhealthy_by_year(df: pd.DataFrame, title: str = "% Tidak Sehat+ per tahun") -> go.Figure:
    yearly = (
        df.groupby("tahun")
        .agg(persen_tidak_sehat_plus=("flag_tidak_sehat_plus", lambda s: pct_true(s)), observasi=("tahun", "size"))
        .reset_index()
    )
    yearly["status"] = yearly["persen_tidak_sehat_plus"].map(risk_level)
    fig = px.bar(
        yearly,
        x="tahun",
        y="persen_tidak_sehat_plus",
        color="status",
        color_discrete_map=RISK_COLORS,
        text=yearly["persen_tidak_sehat_plus"].round(1),
        title=title,
        labels={"tahun": "Tahun", "persen_tidak_sehat_plus": "% Tidak Sehat+", "status": "Status"},
        hover_data={"observasi": True, "status": True, "persen_tidak_sehat_plus": ":.1f"},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_yaxes(range=[0, max(10, yearly["persen_tidak_sehat_plus"].max() * 1.30)])
    fig = apply_fig_style(fig, height=470)
    fig.update_layout(
        title=dict(text=title, y=0.96, x=0.0, xanchor="left", yanchor="top"),
        margin=dict(t=92, r=24, b=86, l=48),
        legend=dict(
            title_text="Status risiko",
            orientation="h",
            yanchor="top",
            y=-0.24,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#1E3448", size=12),
            title_font=dict(color="#102033", size=13, family="Inter, Arial, sans-serif"),
            bordercolor="rgba(15,23,42,0)",
        ),
    )
    return fig


def fig_category_by_year(df: pd.DataFrame, title: str = "Komposisi kategori ISPU per tahun") -> go.Figure:
    yearly_cat = category_counts(df, by=["tahun"], pct=True)
    fig = px.bar(
        yearly_cat,
        x="tahun",
        y="persentase",
        color="categori",
        color_discrete_map=CATEGORY_COLORS,
        category_orders={"categori": CATEGORY_ORDER},
        title=title,
        labels={"tahun": "Tahun", "persentase": "Persentase observasi (%)", "categori": "Kategori"},
        hover_data={"jumlah": True, "persentase": ":.1f"},
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    fig = add_stacked_percent_labels(fig)
    fig = apply_fig_style(fig, height=490)
    fig.update_layout(
        title=dict(text=title, y=0.96, x=0.0, xanchor="left", yanchor="top"),
        margin=dict(t=96, r=24, b=90, l=50),
        legend=dict(
            title_text="",
            orientation="h",
            yanchor="top",
            y=-0.24,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0)",
            font=dict(color="#1E3448", size=12),
            title_font=dict(color="#102033", size=13, family="Inter, Arial, sans-serif"),
            bordercolor="rgba(15,23,42,0)",
        ),
    )
    return fig



def add_station_coordinates(summary: pd.DataFrame) -> pd.DataFrame:
    """Attach approximate SPKU coordinates to station summary data."""
    if summary.empty:
        return pd.DataFrame()
    map_df = summary.copy()
    if "kode" not in map_df.columns:
        map_df["kode"] = map_df["stasiun"].map(station_code)
    map_df["lat"] = map_df["kode"].map(lambda kode: STATION_COORDINATES.get(str(kode), {}).get("lat"))
    map_df["lon"] = map_df["kode"].map(lambda kode: STATION_COORDINATES.get(str(kode), {}).get("lon"))
    map_df["lokasi_ringkas"] = map_df["kode"].map(lambda kode: STATION_COORDINATES.get(str(kode), {}).get("lokasi_ringkas", "—"))
    map_df["wilayah"] = map_df["kode"].map(lambda kode: STATION_COORDINATES.get(str(kode), {}).get("wilayah", "—"))
    map_df = map_df.dropna(subset=["lat", "lon"]).copy()
    if map_df.empty:
        return map_df
    map_df["marker_size"] = 16 + (map_df["persen_tidak_sehat_plus"].fillna(0).clip(lower=0, upper=60) / 60 * 32)
    map_df["marker_color"] = map_df["status_risiko"].map(lambda x: RISK_COLORS.get(x, "#64748B"))
    map_df["tooltip"] = (
        "<b>" + map_df["stasiun"].astype(str) + "</b><br>"
        + "Wilayah: " + map_df["wilayah"].astype(str) + "<br>"
        + "Status Risiko: " + map_df["status_risiko"].astype(str) + "<br>"
        + "Rata-rata ISPU: " + map_df["rata_rata_ispu"].map(lambda v: fmt_float(v, 1)) + "<br>"
        + "Tidak Sehat+: " + map_df["persen_tidak_sehat_plus"].map(lambda v: fmt_pct(v, 1)) + "<br>"
        + "Kategori Dominan: " + map_df["kategori_dominan"].astype(str) + "<br>"
        + "Pencemar Dominan: " + map_df["pencemar_dominan"].astype(str) + "<br>"
        + "Observasi aktif: " + map_df["observasi"].map(fmt_int)
    )
    return map_df


def fig_station_map(summary: pd.DataFrame) -> go.Figure:
    """Interactive point map for SPKU stations.

    Methodological guardrail: this is a point map of monitoring stations. It does
    not color all Jakarta administrative areas and does not interpolate pollution
    between stations.
    """
    map_df = add_station_coordinates(summary)
    fig = go.Figure()
    if map_df.empty:
        fig.update_layout(
            title="Peta titik SPKU Jakarta",
            annotations=[dict(text="Koordinat stasiun tidak tersedia", showarrow=False, x=0.5, y=0.5)],
            height=500,
        )
        return apply_fig_style(fig, height=500, legend=False)

    # Keep a consistent legend order for easier decision reading.
    ordered_status = ["Prioritas Tinggi", "Prioritas Menengah", "Prioritas Pemantauan", "Tidak Ada Data"]
    for status in ordered_status:
        g = map_df[map_df["status_risiko"].eq(status)]
        if g.empty:
            continue
        fig.add_trace(
            go.Scattermapbox(
                lat=g["lat"],
                lon=g["lon"],
                mode="markers+text",
                name=status,
                text=g["kode"],
                textposition="top center",
                textfont=dict(color="#102033", size=13, family="Inter, Arial, sans-serif"),
                marker=dict(
                    size=g["marker_size"],
                    color=RISK_COLORS.get(status, "#64748B"),
                    opacity=0.86,
                ),
                customdata=np.stack(
                    [
                        g["tooltip"],
                    ],
                    axis=-1,
                ),
                hovertemplate="%{customdata[0]}<extra></extra>",
            )
        )

    fig.update_layout(
        title="Peta titik SPKU Jakarta berdasarkan risiko Tidak Sehat+",
        height=540,
        margin=dict(t=88, r=20, b=78, l=20),
        font=dict(family="Inter, Arial, sans-serif", color="#102033", size=12),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=-6.245, lon=106.835),
            zoom=9.65,
            bearing=0,
            pitch=0,
        ),
        legend=dict(
            title=dict(text="Status risiko", font=dict(color="#102033", size=12)),
            orientation="h",
            yanchor="top",
            y=-0.03,
            xanchor="left",
            x=0,
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="rgba(15,23,42,0.12)",
            borderwidth=1,
            font=dict(color="#102033", size=12),
        ),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="rgba(15,23,42,.22)", font_color="#102033"),
    )
    return fig

def fig_station_risk_bar(summary: pd.DataFrame, title: str = "Ranking risiko per stasiun") -> go.Figure:
    plot_df = summary.sort_values("persen_tidak_sehat_plus", ascending=True).copy()
    plot_df["label"] = plot_df["persen_tidak_sehat_plus"].round(1).astype(str) + "%"
    fig = px.bar(
        plot_df,
        x="persen_tidak_sehat_plus",
        y="kode",
        orientation="h",
        color="status_risiko",
        color_discrete_map=RISK_COLORS,
        text="label",
        title=title,
        labels={"kode": "Stasiun", "persen_tidak_sehat_plus": "% Tidak Sehat+", "status_risiko": "Status risiko"},
        hover_data={"stasiun": True, "rata_rata_ispu": ":.1f", "observasi": True},
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_xaxes(range=[0, max(10, plot_df["persen_tidak_sehat_plus"].max() * 1.25)])
    return apply_fig_style(fig, height=420)


def fig_station_category_stack(df: pd.DataFrame, title: str = "Komposisi kategori ISPU per stasiun") -> go.Figure:
    station_cat = category_counts(df, by=["stasiun"], pct=True)
    station_cat["kode"] = station_cat["stasiun"].map(station_code)
    fig = px.bar(
        station_cat,
        x="kode",
        y="persentase",
        color="categori",
        color_discrete_map=CATEGORY_COLORS,
        category_orders={"categori": CATEGORY_ORDER},
        title=title,
        labels={"kode": "Stasiun", "persentase": "Persentase observasi (%)", "categori": "Kategori"},
        hover_data={"stasiun": True, "jumlah": True, "persentase": ":.1f"},
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    fig = add_stacked_percent_labels(fig)
    return apply_fig_style(fig, height=430)


def fig_station_bubble(summary: pd.DataFrame, title: str = "Peta prioritas stasiun") -> go.Figure:
    plot_df = summary.copy()
    fig = px.scatter(
        plot_df,
        x="rata_rata_ispu",
        y="persen_tidak_sehat_plus",
        size="observasi",
        color="status_risiko",
        text="kode",
        color_discrete_map=RISK_COLORS,
        hover_name="stasiun",
        hover_data={
            "kode": False,
            "rata_rata_ispu": ":.1f",
            "median_ispu": ":.1f",
            "persen_tidak_sehat_plus": ":.1f",
            "pencemar_dominan": True,
            "observasi": True,
        },
        title=title,
        labels={
            "rata_rata_ispu": "Rata-rata ISPU",
            "persen_tidak_sehat_plus": "% Tidak Sehat+",
            "status_risiko": "Status risiko",
        },
    )
    fig.update_traces(textposition="top center", marker=dict(line=dict(width=1.4, color="rgba(255,255,255,.65)")))
    fig.update_yaxes(ticksuffix="%")
    fig.add_vline(
        x=101,
        line_dash="dash",
        line_width=1.5,
        line_color="#EA580C",
        annotation_text="Ambang rata-rata ISPU 101",
        annotation_position="top",
        annotation_font_color="#EA580C",
        annotation_font_size=11,
    )
    return apply_fig_style(fig, height=460)


def fig_trend_line(df: pd.DataFrame, granularity: str, view_mode: str, include_all_thresholds: bool = False) -> go.Figure:
    if granularity == "Harian":
        df_plot = df.copy()
        df_plot["periode"] = df_plot["tanggal_clean"]
        period_col = "periode"
    elif granularity == "Bulanan":
        df_plot = df.copy()
        df_plot["periode"] = pd.to_datetime(df_plot["tahun_bulan"].astype(str) + "-01", errors="coerce")
        period_col = "periode"
    else:
        df_plot = df.copy()
        df_plot["periode"] = pd.to_datetime(df_plot["tahun"].astype(str) + "-01-01", errors="coerce")
        period_col = "periode"

    group_cols = [period_col]
    color_col = None
    if view_mode == "Per stasiun":
        group_cols.append("stasiun")
        color_col = "stasiun"

    trend = (
        df_plot.groupby(group_cols)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat_plus=("flag_tidak_sehat_plus", lambda s: pct_true(s)), observasi=("max", "size"))
        .reset_index()
        .sort_values(period_col)
    )

    fig = px.line(
        trend,
        x=period_col,
        y="rata_rata_ispu",
        color=color_col,
        markers=(granularity != "Harian"),
        title=f"Tren rata-rata ISPU · {granularity.lower()} · {view_mode.lower()}",
        labels={period_col: "Periode", "rata_rata_ispu": "Rata-rata ISPU", "stasiun": "Stasiun"},
        hover_data={"persen_tidak_sehat_plus": ":.1f", "observasi": True},
    )
    fig.update_traces(line=dict(width=2.6), marker=dict(size=7))
    fig = add_threshold_lines(fig, include_all=include_all_thresholds)
    fig = add_context_annotations(fig, df_plot)
    return apply_fig_style(fig, height=520)


def fig_critical_by_station(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby(["stasiun", "critical"])
        .size()
        .reset_index(name="jumlah")
    )
    data["kode"] = data["stasiun"].map(station_code)
    data["persentase"] = data["jumlah"] / data.groupby("stasiun")["jumlah"].transform("sum") * 100
    fig = px.bar(
        data,
        x="kode",
        y="persentase",
        color="critical",
        color_discrete_map=CRITICAL_COLORS,
        title="Komposisi pencemar kritis per stasiun",
        labels={"kode": "Stasiun", "persentase": "Persentase (%)", "critical": "Pencemar"},
        hover_data={"stasiun": True, "jumlah": True, "persentase": ":.1f"},
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    fig = add_stacked_percent_labels(fig)
    return apply_fig_style(fig, height=430)


def fig_critical_trend_year(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby(["tahun", "critical"])
        .size()
        .reset_index(name="jumlah")
    )
    data["persentase"] = data["jumlah"] / data.groupby("tahun")["jumlah"].transform("sum") * 100
    # Use a stacked bar instead of area for yearly composition. It avoids
    # confusing decimal year ticks (e.g. 2022.5) and remains readable when the
    # filter contains only one or two years.
    data["tahun"] = data["tahun"].astype(str)
    fig = px.bar(
        data,
        x="tahun",
        y="persentase",
        color="critical",
        color_discrete_map=CRITICAL_COLORS,
        title="Perubahan komposisi pencemar kritis per tahun",
        labels={"tahun": "Tahun", "persentase": "Persentase (%)", "critical": "Pencemar"},
        hover_data={"jumlah": True, "persentase": ":.1f"},
    )
    fig.update_layout(barmode="stack")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    fig = add_stacked_percent_labels(fig)
    return apply_fig_style(fig, height=430)


def fig_critical_heatmap(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby(["stasiun", "critical"])
        .size()
        .reset_index(name="jumlah")
    )
    data["kode"] = data["stasiun"].map(station_code)
    pivot = data.pivot_table(index="kode", columns="critical", values="jumlah", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(
        columns=[c for c in ["PM10", "PM25", "SO2", "CO", "O3", "NO2"] if c in pivot.columns]
        + [c for c in pivot.columns if c not in ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]]
    )
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=["#F8FAFC", "#DBEAFE", "#FEF3C7", "#FDBA74", "#FB7185"],
        title="Heatmap critical: stasiun × parameter",
        labels=dict(x="Pencemar", y="Stasiun", color="Jumlah"),
    )
    fig.update_traces(
        text=pivot.values,
        texttemplate="%{z}",
        textfont=dict(color="#102033", size=12, family="JetBrains Mono, Inter, Arial, sans-serif"),
        hovertemplate="Stasiun: %{y}<br>Pencemar: %{x}<br>Jumlah: %{z}<extra></extra>",
    )
    fig.update_layout(
        coloraxis_colorbar=dict(
            title=dict(text="Jumlah", font=dict(color="#102033", size=13), side="right"),
            tickfont=dict(color="#102033", size=12),
            bgcolor="rgba(255,255,255,0.98)",
            outlinecolor="rgba(15,23,42,0.28)",
            outlinewidth=1,
            thickness=18,
            len=0.70,
        )
    )
    return apply_fig_style(fig, height=460, legend=False)


def fig_seasonal_heatmap(df: pd.DataFrame, metric: str) -> go.Figure:
    if metric == "Rata-rata ISPU":
        data = df.groupby(["tahun", "nama_bulan"], observed=True).agg(nilai=("max", "mean")).reset_index()
        color_label = "Rata-rata ISPU"
        scale = ["#F8FAFC", "#BAE6FD", "#FDE68A", "#FDBA74", "#F43F5E"]
    else:
        data = df.groupby(["tahun", "nama_bulan"], observed=True).agg(nilai=("flag_tidak_sehat_plus", lambda s: pct_true(s))).reset_index()
        color_label = "% Tidak Sehat+"
        scale = ["#F8FAFC", "#DCFCE7", "#FDE68A", "#FDBA74", "#F43F5E"]

    data["nama_bulan"] = pd.Categorical(data["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    pivot = data.pivot_table(index="tahun", columns="nama_bulan", values="nilai", aggfunc="mean")
    pivot = pivot.reindex(columns=MONTH_ORDER)
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=scale,
        title=f"Peta panas pola musiman · {metric.lower()}",
        labels=dict(x="Bulan", y="Tahun", color=color_label),
    )
    fig.update_traces(hovertemplate="Tahun: %{y}<br>Bulan: %{x}<br>Nilai: %{z:.1f}<extra></extra>")
    return apply_fig_style(fig, height=520, legend=False)


def fig_monthly_bars(df: pd.DataFrame, metric: str) -> go.Figure:
    if metric == "Rata-rata ISPU":
        data = df.groupby("nama_bulan", observed=True).agg(nilai=("max", "mean"), observasi=("max", "size")).reset_index()
        title = "Rata-rata ISPU per bulan"
        ylabel = "Rata-rata ISPU"
        color = data["nilai"].map(calc_category_from_ispu)
        data["status"] = color
        cmap = CATEGORY_COLORS
    else:
        data = df.groupby("nama_bulan", observed=True).agg(nilai=("flag_tidak_sehat_plus", lambda s: pct_true(s)), observasi=("max", "size")).reset_index()
        title = "% Tidak Sehat+ per bulan"
        ylabel = "% Tidak Sehat+"
        data["status"] = data["nilai"].map(risk_level)
        cmap = RISK_COLORS

    data["nama_bulan"] = pd.Categorical(data["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    data = data.sort_values("nama_bulan")
    fig = px.bar(
        data,
        x="nama_bulan",
        y="nilai",
        color="status",
        color_discrete_map=cmap,
        text=data["nilai"].round(1),
        title=title,
        labels={"nama_bulan": "Bulan", "nilai": ylabel, "status": "Status"},
        hover_data={"observasi": True, "nilai": ":.1f"},
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", cliponaxis=False)
    fig.update_xaxes(tickangle=-35)
    fig.update_yaxes(range=[0, max(10, data["nilai"].max() * 1.25)])
    if metric == "Rata-rata ISPU":
        fig = add_threshold_lines(fig)
    else:
        fig.update_yaxes(ticksuffix="%")
    return apply_fig_style(fig, height=430)


def fig_monthly_station_line(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby(["nama_bulan", "stasiun"], observed=True)
        .agg(rata_rata_ispu=("max", "mean"), persen_tidak_sehat_plus=("flag_tidak_sehat_plus", lambda s: pct_true(s)), observasi=("max", "size"))
        .reset_index()
    )
    data["nama_bulan"] = pd.Categorical(data["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    data = data.sort_values("nama_bulan")
    data["kode"] = data["stasiun"].map(station_code)
    fig = px.line(
        data,
        x="nama_bulan",
        y="rata_rata_ispu",
        color="kode",
        markers=True,
        title="Pola bulanan rata-rata ISPU per stasiun",
        labels={"nama_bulan": "Bulan", "rata_rata_ispu": "Rata-rata ISPU", "kode": "Stasiun"},
        hover_data={"stasiun": True, "persen_tidak_sehat_plus": ":.1f", "observasi": True},
    )
    fig.update_traces(line=dict(width=2.4), marker=dict(size=7))
    fig.update_xaxes(tickangle=-35)
    fig = add_threshold_lines(fig)
    return apply_fig_style(fig, height=440)


# =============================================================================
# PAGES
# =============================================================================


def page_overview(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Konteks keputusan", "Seberapa serius kondisi udara pada periode aktif, di mana lokasi prioritas, dan pencemar apa yang perlu segera diperhatikan? Angka dihitung dari observasi tanggal-stasiun pada filter aktif.")

    avg_ispu = df["max"].mean()
    median_ispu = df["max"].median()
    unhealthy = pct_true(df["flag_tidak_sehat_plus"])
    top_category = mode_or_dash(df["categori"])
    top_critical = mode_or_dash(df["critical"])
    stations = station_summary(df)
    top_station = stations.iloc[0] if not stations.empty else None

    section_title("Napas Kota Terkini")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Rata-rata ISPU", fmt_float(avg_ispu, 1), note=ispu_status_from_average(avg_ispu), accent=CATEGORY_COLORS.get(ispu_status_from_average(avg_ispu), "#00A676"))
    with c2:
        kpi_card("Median ISPU", fmt_float(median_ispu, 1), note="kondisi tipikal", accent="#0284C7")
    with c3:
        kpi_card("Tidak Sehat+", fmt_pct(unhealthy, 1), note=f"dari {obs_context(df)}", accent="#F97316")
    with c4:
        kpi_card("Kategori dominan", top_category, note="paling sering muncul", accent=CATEGORY_COLORS.get(top_category, "#64748B"))
    with c5:
        kpi_card("Stasiun prioritas", station_code(top_station["stasiun"]) if top_station is not None else "—", note=(top_station["stasiun"] if top_station is not None else "—"), accent="#E11D48")
    with c6:
        kpi_card("Pencemar dominan", top_critical, note="critical paling sering", accent=CRITICAL_COLORS.get(top_critical, "#64748B"))

    section_title("Komposisi risiko dan pencemar utama")
    left, right = st.columns([1.1, 1])
    with left:
        st.plotly_chart(fig_category_distribution(df), use_container_width=True, config=PLOTLY_CONFIG)
    with right:
        st.plotly_chart(fig_critical_distribution(df), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Ringkasan prioritas per stasiun")
    table = stations.copy()
    table = table[["kode", "stasiun", "observasi", "rata_rata_ispu", "median_ispu", "persen_tidak_sehat_plus", "kategori_dominan", "pencemar_dominan", "status_risiko"]]
    table = table.rename(columns={
        "kode": "Kode",
        "stasiun": "Stasiun",
        "observasi": "Observasi",
        "rata_rata_ispu": "Rata-rata ISPU",
        "median_ispu": "Median ISPU",
        "persen_tidak_sehat_plus": "% Tidak Sehat+",
        "kategori_dominan": "Kategori Dominan",
        "pencemar_dominan": "Pencemar Dominan",
        "status_risiko": "Status Risiko",
    })
    render_light_table(
        table,
        progress_cols=["% Tidak Sehat+"],
        numeric_cols=["Rata-rata ISPU", "Median ISPU"],
        int_cols=["Observasi"],
        chip_cols=["Kategori Dominan", "Pencemar Dominan", "Status Risiko"],
        long_cols=["Stasiun"],
        max_height=380,
    )

    top_station_name = top_station["stasiun"] if top_station is not None else "—"
    top_station_pct = top_station["persen_tidak_sehat_plus"] if top_station is not None else np.nan
    top3_stations = top_station_rank_text(stations)
    response_level, response_action = response_action_by_risk(unhealthy)
    insight_panel(
        "Insight eksekutif",
        decision_grade_body(
            temuan=f"Berdasarkan <b>{obs_context_active(df)}</b>, kategori dominan adalah <b>{top_category}</b>, rata-rata ISPU <b>{fmt_float(avg_ispu, 1)}</b>, dan observasi <b>Tidak Sehat+</b> sebesar <b>{fmt_pct(unhealthy, 1)}</b>.",
            makna=f"Status respons periode aktif adalah <b>{response_level}</b>. Tiga lokasi prioritas berdasarkan frekuensi Tidak Sehat+ adalah <b>{top3_stations}</b>; lokasi teratas adalah <b>{top_station_name}</b> dengan <b>{fmt_pct(top_station_pct, 1)}</b>.",
            tindakan=f"{response_action.capitalize()} Dalami <b>{top_critical}</b> pada menu Pencemar Kritis dan cek periode rawan pada menu Pola Musiman sebelum menetapkan intervensi.",
            batasan="Angka menggambarkan observasi tanggal-stasiun pada filter aktif, bukan status udara real-time dan bukan klaim keterwakilan seluruh wilayah Jakarta.",
        ),
    )

    insight_panel(
        "Prioritas keputusan cepat",
        f"Mulai dari <b>lokasi prioritas</b> ({top_station_name}), lalu cek <b>pencemar dominan</b> ({top_critical}), kemudian tentukan <b>periode antisipasi</b> pada dashboard musiman. Alur ini membantu keputusan bergerak dari kondisi umum → lokasi → parameter → waktu tindakan.",
    )

    download_filtered_data(df, "ispu_jakarta_filtered_overview.csv")


def page_trend(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Konteks keputusan", "Apakah kualitas udara sedang membaik, memburuk, atau fluktuatif; dan kapan nilai ISPU melewati ambang Tidak Sehat? Persentase risiko menggunakan observasi tanggal-stasiun sebagai denominator.")

    control_a, control_b, control_c = st.columns([1.1, 1.1, 1])
    with control_a:
        granularity = st.radio("Granularitas tren", ["Bulanan", "Tahunan", "Harian"], horizontal=True, index=0)
    with control_b:
        view_mode = st.radio("Mode tampilan", ["Agregat Jakarta", "Per stasiun"], horizontal=True, index=0)
    with control_c:
        include_all_thresholds = st.checkbox("Tampilkan semua threshold", value=False)

    max_year = int(df["tahun"].max())
    cur_avg, prev_avg, delta_avg = previous_year_value(df, max_year, "max", "mean")
    cur_unhealthy, prev_unhealthy, delta_unhealthy = previous_year_value(df, max_year, "flag_tidak_sehat_plus", "pct_true")

    section_title("Sinyal Terkini Tahun Terakhir")
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card("Tahun terakhir", str(max_year), note="dalam data terfilter", accent="#0284C7")
    with k2:
        kpi_card("Rata-rata ISPU", fmt_float(cur_avg, 1), delta=(f"vs {max_year-1}: {fmt_float(delta_avg,1)}" if not pd.isna(delta_avg) else ""), accent=CATEGORY_COLORS.get(ispu_status_from_average(cur_avg), "#00A676"))
    with k3:
        kpi_card("Tidak Sehat+", fmt_pct(cur_unhealthy, 1), delta=(f"vs {max_year-1}: {fmt_pct(delta_unhealthy,1)}" if not pd.isna(delta_unhealthy) else ""), note=f"{fmt_int(len(df[df['tahun'] == max_year]))} observasi tahun {max_year}", accent="#F97316")
    with k4:
        worst_year_df = (
            df.groupby("tahun")
            .agg(persen_tidak_sehat_plus=("flag_tidak_sehat_plus", lambda s: pct_true(s)))
            .reset_index()
            .sort_values("persen_tidak_sehat_plus", ascending=False)
        )
        worst_year = worst_year_df.iloc[0] if not worst_year_df.empty else None
        kpi_card("Tahun risiko tertinggi", str(int(worst_year["tahun"])) if worst_year is not None else "—", note=(fmt_pct(worst_year["persen_tidak_sehat_plus"], 1) if worst_year is not None else "—"), accent="#E11D48")

    section_title("Tren ISPU dengan ambang Tidak Sehat")
    st.plotly_chart(fig_trend_line(df, granularity, view_mode, include_all_thresholds), use_container_width=True, config=PLOTLY_CONFIG)
    pm25_year = first_available_year(df, "pm25")
    context_note = "Grafik tren diberi anotasi periode khusus seperti COVID-19 sebagai konteks interpretasi, bukan bukti sebab-akibat."
    if pm25_year is not None:
        context_note += f" PM2.5 mulai tersedia pada filter aktif sejak {pm25_year}; pembacaan pencemar sebelum periode tersebut perlu berhati-hati."
    insight_panel("Konteks pembacaan tren", context_note, kind="warning")

    left, right = st.columns(2)
    with left:
        st.plotly_chart(fig_unhealthy_by_year(df), use_container_width=True, config=PLOTLY_CONFIG)
    with right:
        st.plotly_chart(fig_category_by_year(df), use_container_width=True, config=PLOTLY_CONFIG)

    trend_direction = "memburuk" if not pd.isna(delta_unhealthy) and delta_unhealthy > 0 else "membaik/menurun" if not pd.isna(delta_unhealthy) and delta_unhealthy < 0 else "relatif stabil atau belum dapat dibandingkan"
    historical_unhealthy = pct_true(df["flag_tidak_sehat_plus"])
    trend_context = trend_context_text(cur_unhealthy, prev_unhealthy, historical_unhealthy)
    response_level, response_action = response_action_by_risk(cur_unhealthy)
    yearly_rank = worst_year_df.head(3) if not worst_year_df.empty else pd.DataFrame()
    top_years = join_ranked_items([f"{int(row['tahun'])} ({fmt_pct(row['persen_tidak_sehat_plus'], 1)})" for _, row in yearly_rank.iterrows()])
    insight_panel(
        "Insight tren",
        decision_grade_body(
            temuan=f"Pada tahun terakhir dalam filter ({max_year}), terdapat <b>{fmt_int(len(df[df['tahun'] == max_year]))} observasi tanggal-stasiun</b> dengan rata-rata ISPU <b>{fmt_float(cur_avg, 1)}</b> dan frekuensi Tidak Sehat+ <b>{fmt_pct(cur_unhealthy, 1)}</b>.",
            makna=f"Kondisi tahun terakhir terlihat <b>{trend_direction}</b>; konteks pembanding menunjukkan angka tersebut {trend_context} Tahun dengan risiko tertinggi dalam filter adalah <b>{top_years}</b>.",
            tindakan=f"Untuk status <b>{response_level}</b>, {response_action} Periode yang konsisten melewati threshold ISPU 101 perlu menjadi target evaluasi program pengendalian emisi.",
            batasan="Tren historis membantu membaca pola dan evaluasi, tetapi tidak boleh dibaca sebagai prediksi masa depan tanpa model dan variabel tambahan.",
        ),
    )
    insight_panel(
        "Arahan tindakan",
        "Gunakan tren tahun terakhir sebagai sinyal operasional, lalu bandingkan dengan tahun sebelumnya dan rata-rata historis. Jika pemburukan berulang, koordinasikan evaluasi sumber emisi pada stasiun prioritas dan bulan yang paling sering melewati ambang Tidak Sehat.",
    )


def page_station(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Konteks keputusan", "Stasiun mana yang harus menjadi prioritas pengendalian pencemaran berdasarkan frekuensi risiko dan tekanan ISPU? Perbandingan memakai persentase per stasiun agar lebih adil.")

    summary = station_summary(df)
    if summary.empty:
        empty_state()
        return

    top = summary.iloc[0]
    bottom = summary.iloc[-1]
    gap = top["persen_tidak_sehat_plus"] - bottom["persen_tidak_sehat_plus"]

    section_title("Peta Risiko Lokasi")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Stasiun risiko tertinggi", station_code(top["stasiun"]), note=top["stasiun"], accent="#E11D48")
    with c2:
        kpi_card("Tidak Sehat+ tertinggi", fmt_pct(top["persen_tidak_sehat_plus"], 1), note=top["status_risiko"], accent="#F97316")
    with c3:
        kpi_card("Stasiun risiko terendah", station_code(bottom["stasiun"]), note=bottom["stasiun"], accent="#00A676")
    with c4:
        kpi_card("Kesenjangan risiko", fmt_pct(gap, 1), note="selisih tertinggi vs terendah", accent="#F4B400")

    section_title("Peta Interaktif SPKU Jakarta")
    page_brief(
        "Catatan peta",
        "Peta menampilkan titik stasiun pemantau kualitas udara. Warna marker menunjukkan status risiko, ukuran marker menunjukkan frekuensi Tidak Sehat+. Peta ini bukan pewarnaan seluruh wilayah Jakarta dan tidak melakukan interpolasi sebaran polusi.",
    )
    map_left, map_right = st.columns([1.55, 0.85])
    with map_left:
        st.plotly_chart(fig_station_map(summary), use_container_width=True, config=PLOTLY_CONFIG)
    with map_right:
        insight_panel(
            "Lokasi prioritas pada peta",
            f"Titik <b>{top['stasiun']}</b> menjadi prioritas karena memiliki frekuensi Tidak Sehat+ tertinggi sebesar <b>{fmt_pct(top['persen_tidak_sehat_plus'], 1)}</b> pada filter aktif. Marker pada peta hanya merepresentasikan lokasi SPKU, sehingga arahan kebijakan tetap perlu dikombinasikan dengan validasi lapangan dan data sumber emisi sekitar stasiun.",
        )
        insight_panel(
            "Guardrail interpretasi",
            "Jangan membaca warna marker sebagai kondisi seluruh kecamatan/kota administratif. Warna hanya menunjukkan ringkasan risiko pada titik SPKU yang tersedia di dataset.",
            kind="warning",
        )

    section_title("Perbandingan risiko antar SPKU")
    left, right = st.columns([1, 1.05])
    with left:
        st.plotly_chart(fig_station_risk_bar(summary), use_container_width=True, config=PLOTLY_CONFIG)
    with right:
        st.plotly_chart(fig_station_bubble(summary), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Komposisi kategori per stasiun")
    st.plotly_chart(fig_station_category_stack(df), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Tabel ringkas keputusan lokasi")
    table = summary[["kode", "stasiun", "observasi", "rata_rata_ispu", "persen_tidak_sehat_plus", "kategori_dominan", "pencemar_dominan", "status_risiko"]].copy()
    table = table.rename(columns={
        "kode": "Kode",
        "stasiun": "Stasiun",
        "observasi": "Observasi",
        "rata_rata_ispu": "Rata-rata ISPU",
        "persen_tidak_sehat_plus": "% Tidak Sehat+",
        "kategori_dominan": "Kategori Dominan",
        "pencemar_dominan": "Pencemar Dominan",
        "status_risiko": "Status Risiko",
    })
    render_light_table(
        table,
        progress_cols=["% Tidak Sehat+"],
        numeric_cols=["Rata-rata ISPU"],
        int_cols=["Observasi"],
        chip_cols=["Kategori Dominan", "Pencemar Dominan", "Status Risiko"],
        long_cols=["Stasiun"],
        max_height=380,
    )

    top3_stations = top_station_rank_text(summary)
    high_count = int((summary["status_risiko"] == "Prioritas Tinggi").sum())
    mid_count = int((summary["status_risiko"] == "Prioritas Menengah").sum())
    response_level, response_action = response_action_by_risk(top["persen_tidak_sehat_plus"])
    insight_panel(
        "Insight lokasi",
        decision_grade_body(
            temuan=f"Stasiun <b>{top['stasiun']}</b> memiliki frekuensi Tidak Sehat+ tertinggi sebesar <b>{fmt_pct(top['persen_tidak_sehat_plus'], 1)}</b>. Tiga stasiun prioritas adalah <b>{top3_stations}</b>.",
            makna=f"Terdapat <b>{fmt_int(high_count)}</b> stasiun prioritas tinggi dan <b>{fmt_int(mid_count)}</b> stasiun prioritas menengah pada filter aktif. Kesenjangan risiko tertinggi-terendah sebesar <b>{fmt_pct(gap, 1)}</b> menunjukkan bahwa respons sebaiknya spesifik lokasi, bukan seragam.",
            tindakan=f"Untuk lokasi teratas dengan status <b>{response_level}</b>, {response_action} Kaitkan hasil ini dengan pencemar dominan per stasiun sebelum menyusun inspeksi/validasi lapangan.",
            batasan=f"Perbandingan memakai persentase dari observasi tanggal-stasiun pada masing-masing stasiun; peta hanya titik SPKU dan tidak mewakili seluruh wilayah administratif.",
        ),
    )
    insight_panel(
        "Arahan tindakan",
        "Susun prioritas berjenjang: Prioritas Tinggi untuk validasi lapangan dan evaluasi sumber emisi, Prioritas Menengah untuk pemantauan tren berkala, dan Prioritas Pemantauan sebagai baseline pembanding kualitas udara.",
    )


def page_critical(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Konteks keputusan", "Parameter pencemar apa yang paling sering mendorong risiko kualitas udara dan perlu menjadi fokus pengendalian? Critical dibaca sebagai parameter pembentuk indeks tertinggi, bukan konsentrasi fisik terbesar.")

    pm25_year_full = first_available_year(full_df, "pm25")
    mode_options = ["Semua data aktif", "Sejak PM2.5 tersedia", "Observasi dengan semua parameter tersedia"]
    analysis_mode = st.radio(
        "Mode pembacaan pencemar kritis",
        options=mode_options,
        horizontal=True,
        index=0,
        help="Gunakan mode sejak PM2.5 tersedia atau observasi lengkap untuk pembandingan polutan yang lebih adil.",
    )
    analysis_df = df.copy()
    mode_note = "Mode semua data aktif digunakan untuk gambaran umum."
    if analysis_mode == "Sejak PM2.5 tersedia":
        if pm25_year_full is not None:
            analysis_df = analysis_df[analysis_df["tahun"] >= pm25_year_full].copy()
            mode_note = f"Analisis dibatasi sejak PM2.5 tersedia ({pm25_year_full}) agar dominasi pencemar tidak bias oleh ketiadaan data PM2.5 pada periode awal."
        else:
            mode_note = "PM2.5 tidak tersedia pada dataset, sehingga mode ini tetap memakai data aktif."
    elif analysis_mode == "Observasi dengan semua parameter tersedia":
        available_cols = [c for c in POLLUTANT_COLS if c in analysis_df.columns]
        if available_cols:
            analysis_df = analysis_df.dropna(subset=available_cols).copy()
            mode_note = "Analisis dibatasi pada observasi dengan seluruh parameter pencemar tersedia agar pembandingan antar parameter lebih seimbang."
    insight_panel("Mode pembacaan adil", mode_note, kind="warning")

    crit_df = analysis_df[analysis_df["critical"].notna() & (analysis_df["critical"] != "TIDAK ADA DATA")].copy()
    if crit_df.empty:
        st.warning("Tidak ada data pencemar kritis yang tersedia pada mode/filter aktif. Coba gunakan mode 'Semua data aktif' atau longgarkan filter.")
        return

    top_crit = mode_or_dash(crit_df["critical"])
    top_crit_count = int((crit_df["critical"] == top_crit).sum()) if top_crit != "—" else 0
    top_crit_pct = top_crit_count / max(len(crit_df), 1) * 100
    unhealthy_crit = crit_df[crit_df["flag_tidak_sehat_plus"]]
    top_crit_unhealthy = mode_or_dash(unhealthy_crit["critical"])
    multi_share = pct_true(crit_df.get("flag_multi_critical", pd.Series(False, index=crit_df.index))) if "flag_multi_critical" in crit_df.columns else 0

    section_title("Jejak Pencemar Dominan")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Pencemar dominan", top_crit, note=f"{fmt_pct(top_crit_pct, 1)} dari data critical", accent=CRITICAL_COLORS.get(top_crit, "#00A676"))
    with c2:
        kpi_card("Critical valid", fmt_int(len(crit_df)), note="observasi tanggal-stasiun dengan critical", accent="#0284C7")
    with c3:
        kpi_card("Dominan saat Tidak Sehat+", top_crit_unhealthy, note="khusus risiko tinggi", accent=CRITICAL_COLORS.get(top_crit_unhealthy, "#F97316"))
    with c4:
        kpi_card("Multi-critical", fmt_pct(multi_share, 1), note="kasus pencemar bernilai maksimum sama", accent="#F4B400")

    section_title("Distribusi pencemar kritis")
    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(fig_critical_distribution(crit_df, "Ranking pencemar kritis keseluruhan"), use_container_width=True, config=PLOTLY_CONFIG)
    with right:
        st.plotly_chart(fig_critical_heatmap(crit_df), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Pencemar kritis menurut lokasi dan waktu")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_critical_by_station(crit_df), use_container_width=True, config=PLOTLY_CONFIG)
    with col2:
        st.plotly_chart(fig_critical_trend_year(crit_df), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Pencemar pada kondisi Tidak Sehat+")
    if unhealthy_crit.empty:
        st.info("Tidak ada observasi Tidak Sehat+ pada filter aktif.")
    else:
        st.plotly_chart(fig_critical_distribution(unhealthy_crit, "Pencemar dominan khusus kategori Tidak Sehat+"), use_container_width=True, config=PLOTLY_CONFIG)

    top3_critical = top_critical_rank_text(crit_df)
    policy_guidance = pollutant_policy_guidance(top_crit)
    unhealthy_guidance = pollutant_policy_guidance(top_crit_unhealthy)
    insight_panel(
        "Insight pencemar",
        decision_grade_body(
            temuan=f"Pencemar kritis dominan adalah <b>{top_crit}</b> dengan porsi <b>{fmt_pct(top_crit_pct, 1)}</b> dari <b>{fmt_int(len(crit_df))} observasi tanggal-stasiun yang memiliki critical</b>. Tiga pencemar teratas adalah <b>{top3_critical}</b>.",
            makna=f"Pada observasi Tidak Sehat+, pencemar dominan adalah <b>{top_crit_unhealthy}</b>. Ini mengarahkan kebijakan dari isu umum kualitas udara menjadi fokus parameter yang perlu dikendalikan.",
            tindakan=f"Untuk dominasi <b>{top_crit}</b>, {policy_guidance} Jika fokus khusus pada kondisi Tidak Sehat+, gunakan arahan untuk <b>{top_crit_unhealthy}</b>: {unhealthy_guidance}",
            batasan=f"Mode analisis: {analysis_mode}. Critical adalah parameter pembentuk indeks tertinggi, bukan konsentrasi fisik terbesar dan bukan bukti sebab-akibat tunggal. Analisis lanjutan perlu data sumber emisi, meteorologi, dan validasi lapangan.",
        ),
    )
    insight_panel(
        "Catatan interpretasi",
        "Analisis PM2.5 perlu dibaca bersama ketersediaan historis datanya. Jika satu parameter belum tersedia di seluruh periode, pembandingan lintas tahun perlu menggunakan persentase pada periode yang memiliki data, bukan jumlah mentah semata.",
        kind="warning",
    )


def page_seasonal(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Konteks keputusan", "Bulan apa yang menjadi periode rawan dan kapan Dinas perlu meningkatkan pemantauan serta komunikasi risiko? Pola musiman dibaca dari observasi tanggal-stasiun pada filter aktif.")

    monthly = df.groupby("nama_bulan", observed=True).agg(
        rata_rata_ispu=("max", "mean"),
        persen_tidak_sehat_plus=("flag_tidak_sehat_plus", lambda s: pct_true(s)),
        observasi=("max", "size"),
        pencemar_dominan=("critical", mode_or_dash),
    ).reset_index()
    monthly["nama_bulan"] = pd.Categorical(monthly["nama_bulan"], categories=MONTH_ORDER, ordered=True)
    monthly = monthly.sort_values("nama_bulan")

    worst_avg = monthly.sort_values("rata_rata_ispu", ascending=False).iloc[0]
    worst_risk = monthly.sort_values("persen_tidak_sehat_plus", ascending=False).iloc[0]
    best_avg = monthly.sort_values("rata_rata_ispu", ascending=True).iloc[0]

    section_title("Kalender Risiko Udara")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card("Bulan ISPU tertinggi", str(worst_avg["nama_bulan"]), note=f"Rata-rata {fmt_float(worst_avg['rata_rata_ispu'],1)}", accent="#E11D48")
    with c2:
        kpi_card("Bulan Tidak Sehat+ tertinggi", str(worst_risk["nama_bulan"]), note=fmt_pct(worst_risk["persen_tidak_sehat_plus"], 1), accent="#F97316")
    with c3:
        kpi_card("Bulan relatif terbaik", str(best_avg["nama_bulan"]), note=f"Rata-rata {fmt_float(best_avg['rata_rata_ispu'],1)}", accent="#00A676")
    with c4:
        kpi_card("Pencemar bulan rawan", str(worst_risk["pencemar_dominan"]), note=f"pada {worst_risk['nama_bulan']}", accent=CRITICAL_COLORS.get(str(worst_risk["pencemar_dominan"]), "#F4B400"))

    metric = st.radio("Metrik heatmap", ["Rata-rata ISPU", "% Tidak Sehat+"], horizontal=True, index=0)
    st.plotly_chart(fig_seasonal_heatmap(df, metric), use_container_width=True, config=PLOTLY_CONFIG)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(fig_monthly_bars(df, "Rata-rata ISPU"), use_container_width=True, config=PLOTLY_CONFIG)
    with right:
        st.plotly_chart(fig_monthly_bars(df, "% Tidak Sehat+"), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Pola musiman per stasiun")
    st.plotly_chart(fig_monthly_station_line(df), use_container_width=True, config=PLOTLY_CONFIG)

    # Operational calendar table
    calendar = monthly.copy()
    calendar["status_operasional"] = calendar["persen_tidak_sehat_plus"].map(risk_level)
    calendar["arahan"] = np.select(
        [
            calendar["status_operasional"].eq("Prioritas Tinggi"),
            calendar["status_operasional"].eq("Prioritas Menengah"),
        ],
        [
            "Tingkatkan pemantauan, inspeksi sumber emisi, dan komunikasi risiko.",
            "Perkuat pemantauan dan siapkan respons bila tren naik.",
        ],
        default="Pantau rutin dan gunakan sebagai periode evaluasi program.",
    )
    calendar = calendar.rename(columns={
        "nama_bulan": "Bulan",
        "rata_rata_ispu": "Rata-rata ISPU",
        "persen_tidak_sehat_plus": "% Tidak Sehat+",
        "pencemar_dominan": "Pencemar Dominan",
        "status_operasional": "Status Operasional",
        "arahan": "Arahan Operasional",
    })
    section_title("Kalender antisipasi operasional")
    render_light_table(
        calendar[["Bulan", "Rata-rata ISPU", "% Tidak Sehat+", "Pencemar Dominan", "Status Operasional", "Arahan Operasional"]],
        progress_cols=["% Tidak Sehat+"],
        numeric_cols=["Rata-rata ISPU"],
        chip_cols=["Pencemar Dominan", "Status Operasional"],
        long_cols=["Arahan Operasional"],
        max_height=560,
    )

    top3_risk_months = top_month_rank_text(monthly, "persen_tidak_sehat_plus")
    top3_avg_months = top_month_rank_text(monthly, "rata_rata_ispu")
    response_level, response_action = response_action_by_risk(worst_risk["persen_tidak_sehat_plus"])
    insight_panel(
        "Insight musiman",
        decision_grade_body(
            temuan=f"Berdasarkan <b>{obs_context_active(df)}</b>, bulan dengan rata-rata ISPU tertinggi adalah <b>{worst_avg['nama_bulan']}</b>, sedangkan bulan dengan frekuensi Tidak Sehat+ tertinggi adalah <b>{worst_risk['nama_bulan']}</b>. Tiga bulan rawan utama adalah <b>{top3_risk_months}</b>.",
            makna=f"Kalender risiko menunjukkan kapan Dinas perlu bersiap sebelum kualitas udara memburuk. Bulan dengan tekanan ISPU tertinggi adalah <b>{top3_avg_months}</b>, sehingga evaluasi perlu melihat baik rata-rata ISPU maupun frekuensi Tidak Sehat+.",
            tindakan=f"Untuk bulan rawan dengan status <b>{response_level}</b>, {response_action} Terapkan siklus: 1–2 bulan sebelum bulan rawan siapkan pemantauan/komunikasi risiko; saat bulan rawan tingkatkan pengawasan; setelahnya evaluasi efektivitas tindakan.",
            batasan="Pola musiman bersifat deskriptif dan tidak otomatis menjelaskan penyebab. Interpretasi perlu dilengkapi data meteorologi, emisi, dan kondisi aktivitas sumber pencemar.",
        ),
    )
    insight_panel(
        "Arahan tindakan",
        "Gunakan kalender antisipasi sebagai rencana operasional tahunan: bulan prioritas tinggi untuk peningkatan pemantauan dan komunikasi risiko, bulan prioritas menengah untuk kesiapsiagaan, dan bulan pemantauan sebagai periode evaluasi program.",
    )


def page_data_quality(df: pd.DataFrame, full_df: pd.DataFrame, log_df: pd.DataFrame, audit_df: pd.DataFrame, validation_df: pd.DataFrame) -> None:
    if full_df.empty:
        empty_state()
        return

    page_brief("Konteks keputusan", "Apakah data cukup valid, cukup terkini, dan cukup representatif untuk dijadikan dasar keputusan? Menu ini juga membatasi interpretasi agar dashboard tidak dibaca sebagai prediksi atau status real-time.")

    total_final = len(full_df)
    total_filtered = len(df)
    start = full_df["tanggal_clean"].min().strftime("%d %b %Y")
    end = full_df["tanggal_clean"].max().strftime("%d %b %Y")
    final_dup = int(full_df.duplicated(subset=["tanggal_clean", "stasiun"]).sum())
    total_stations = full_df["stasiun"].nunique()
    total_audit = len(audit_df) if not audit_df.empty else 0
    validation_issues = int(validation_df["jumlah_baris_bermasalah"].sum()) if not validation_df.empty and "jumlah_baris_bermasalah" in validation_df.columns else 0
    status = "Layak digunakan" if final_dup == 0 and validation_issues == 0 else "Perlu perhatian"
    status_accent = "#00A676" if status == "Layak digunakan" else "#F4B400"

    section_title("Kepercayaan Data untuk Keputusan")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        kpi_card("Status data", status, note="untuk analisis dashboard", accent=status_accent)
    with c2:
        kpi_card("Periode data", f"{start}<br>{end}", note="historis, bukan real-time", accent="#0284C7")
    with c3:
        kpi_card("Observasi final", fmt_int(total_final), note=f"{fmt_int(total_filtered)} aktif setelah filter", accent="#00A676")
    with c4:
        kpi_card("Stasiun", fmt_int(total_stations), note="SPKU dalam dataset", accent="#F4B400")
    with c5:
        kpi_card("Duplikasi final", fmt_int(final_dup), note=f"audit duplikasi: {fmt_int(total_audit)} baris", accent="#E11D48" if final_dup else "#00A676")

    decision_confidence = decision_confidence_text(status, validation_issues, final_dup, total_filtered)
    insight_panel(
        "Decision Confidence",
        decision_grade_body(
            temuan=f"Status data dashboard adalah <b>{status}</b>. Dataset final berisi <b>{fmt_int(total_final)}</b> observasi, <b>{fmt_int(total_stations)}</b> stasiun, duplikasi final <b>{fmt_int(final_dup)}</b>, dan isu validasi akhir <b>{fmt_int(validation_issues)}</b> baris.",
            makna=decision_confidence,
            tindakan="Gunakan dashboard untuk keputusan strategis dan evaluatif: prioritas lokasi, pencemar dominan, tren historis, dan periode rawan. Untuk keputusan harian/status udara saat ini, gunakan data pemantauan terbaru atau real-time.",
            batasan="Ketersediaan parameter tidak selalu merata sepanjang periode; interpretasi PM2.5, critical, dan tren historis harus dibaca bersama catatan metodologi serta audit data.",
        ),
    )

    section_title("Cakupan Sensor dan Periode")
    col1, col2 = st.columns(2)
    with col1:
        yearly = full_df.groupby("tahun").size().reset_index(name="observasi")
        fig = px.bar(yearly, x="tahun", y="observasi", title="Jumlah observasi per tahun", labels={"tahun": "Tahun", "observasi": "Observasi"})
        fig.update_traces(marker_color="#0284C7", text=yearly["observasi"], textposition="outside", cliponaxis=False)
        st.plotly_chart(apply_fig_style(fig, height=380, legend=False), use_container_width=True, config=PLOTLY_CONFIG)
    with col2:
        station_cov = full_df.groupby("stasiun").size().reset_index(name="observasi")
        station_cov["kode"] = station_cov["stasiun"].map(station_code)
        fig = px.bar(station_cov.sort_values("observasi", ascending=True), x="observasi", y="kode", orientation="h", title="Jumlah observasi per stasiun", labels={"observasi": "Observasi", "kode": "Stasiun"}, hover_data={"stasiun": True})
        fig.update_traces(marker_color="#00A676", text="observasi", textposition="outside", cliponaxis=False)
        st.plotly_chart(apply_fig_style(fig, height=380, legend=False), use_container_width=True, config=PLOTLY_CONFIG)

    section_title("Completeness parameter pencemar")
    available_pollutants = [c for c in POLLUTANT_COLS if c in full_df.columns]
    missing = pd.DataFrame({
        "parameter": [c.upper() for c in available_pollutants],
        "missing": [int(full_df[c].isna().sum()) for c in available_pollutants],
        "missing_pct": [float(full_df[c].isna().mean() * 100) for c in available_pollutants],
        "tersedia_pct": [float(full_df[c].notna().mean() * 100) for c in available_pollutants],
    })
    fig = px.bar(
        missing.sort_values("tersedia_pct"),
        x="tersedia_pct",
        y="parameter",
        orientation="h",
        title="Ketersediaan data per parameter",
        labels={"tersedia_pct": "Ketersediaan (%)", "parameter": "Parameter"},
        text=missing.sort_values("tersedia_pct")["tersedia_pct"].round(1),
    )
    fig.update_traces(marker_color="#F4B400", texttemplate="%{text:.1f}%", textposition="outside", cliponaxis=False)
    fig.update_xaxes(range=[0, 105], ticksuffix="%")
    st.plotly_chart(apply_fig_style(fig, height=420, legend=False), use_container_width=True, config=PLOTLY_CONFIG)
    insight_panel(
        "Catatan batasan data",
        "Ketersediaan parameter tidak selalu sama sepanjang periode historis. Khusus PM2.5, interpretasi lintas tahun perlu mempertimbangkan periode kemunculan data agar Kepala Dinas tidak salah menyimpulkan dominasi atau absennya PM2.5 pada tahun awal.",
        kind="warning",
    )

    section_title("Timeline ketersediaan parameter")
    st.plotly_chart(fig_parameter_availability_heatmap(full_df), use_container_width=True, config=PLOTLY_CONFIG)
    availability_table = parameter_availability_summary(full_df)
    render_light_table(
        availability_table.rename(columns={"Coverage": "Coverage (%)"}),
        progress_cols=["Coverage (%)"],
        int_cols=["Tahun Tersedia"],
        chip_cols=["Status"],
        long_cols=["Catatan Interpretasi"],
        max_height=420,
    )
    pm25_year = first_available_year(full_df, "pm25")
    if pm25_year is not None:
        insight_panel(
            "Konteks PM2.5",
            f"PM2.5 mulai tersedia pada dataset final sejak <b>{pm25_year}</b>. Artinya, ketiadaan dominasi PM2.5 sebelum periode tersebut tidak boleh dibaca sebagai bukti PM2.5 rendah; gunakan mode pembacaan yang adil pada menu Pencemar Kritis untuk membatasi analisis sejak PM2.5 tersedia.",
            kind="warning",
        )

    section_title("Kapan angka tidak boleh dibandingkan langsung?")
    render_light_table(
        comparison_guardrail_table(),
        long_cols=["Kondisi", "Risiko Salah Tafsir", "Cara Baca yang Benar"],
        max_height=480,
    )

    section_title("Hasil Validasi Akhir")
    if validation_df.empty:
        st.info("File validasi final tidak tersedia.")
    else:
        val = validation_df.copy()
        val["status"] = np.where(val["jumlah_baris_bermasalah"] == 0, "Aman", "Perlu perhatian")
        validation_table = val.rename(columns={"aspek_validasi": "Aspek Validasi", "jumlah_baris_bermasalah": "Jumlah Baris Bermasalah", "status": "Status"})
        render_light_table(
            validation_table,
            int_cols=["Jumlah Baris Bermasalah"],
            chip_cols=["Status"],
            long_cols=["Aspek Validasi"],
            max_height=460,
        )

    section_title("Jejak Pembersihan Data")
    if log_df.empty:
        st.info("File cleaning log tidak tersedia.")
    else:
        show_cols = [c for c in ["tahap", "masalah", "kolom_terdampak", "jumlah_baris_terdampak", "strategi_penanganan", "justifikasi", "dampak_setelah_cleaning"] if c in log_df.columns]
        cleaning_table = log_df[show_cols].rename(columns={
            "tahap": "Tahap",
            "masalah": "Masalah",
            "kolom_terdampak": "Kolom Terdampak",
            "jumlah_baris_terdampak": "Jumlah Baris Terdampak",
            "strategi_penanganan": "Strategi Penanganan",
            "justifikasi": "Justifikasi",
            "dampak_setelah_cleaning": "Dampak Setelah Cleaning",
        })
        render_light_table(
            cleaning_table,
            int_cols=["Jumlah Baris Terdampak"],
            long_cols=["Masalah", "Kolom Terdampak", "Strategi Penanganan", "Justifikasi", "Dampak Setelah Cleaning"],
            max_height=560,
        )

    section_title("Audit duplikasi tanggal-stasiun")
    if audit_df.empty:
        st.info("File audit duplikasi tidak tersedia atau tidak ada baris audit.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            if "dedup_action" in audit_df.columns:
                act = audit_df.groupby("dedup_action").size().reset_index(name="jumlah")
                fig = px.bar(act, x="dedup_action", y="jumlah", title="Status penanganan duplikasi", labels={"dedup_action": "Tindakan", "jumlah": "Jumlah"}, text="jumlah")
                fig.update_traces(marker_color="#7C3AED", textposition="outside", cliponaxis=False)
                st.plotly_chart(apply_fig_style(fig, height=360, legend=False), use_container_width=True, config=PLOTLY_CONFIG)
        with col2:
            if "duplicate_type" in audit_df.columns:
                typ = audit_df.groupby("duplicate_type").size().reset_index(name="jumlah")
                fig = px.bar(typ, x="duplicate_type", y="jumlah", title="Jenis duplikasi", labels={"duplicate_type": "Jenis", "jumlah": "Jumlah"}, text="jumlah")
                fig.update_traces(marker_color="#F97316", textposition="outside", cliponaxis=False)
                st.plotly_chart(apply_fig_style(fig, height=360, legend=False), use_container_width=True, config=PLOTLY_CONFIG)
        show_cols = [c for c in ["duplicate_group_id", "tanggal", "stasiun", "max", "critical", "categori", "duplicate_type", "dedup_action", "used_for_main_dashboard_kpi"] if c in audit_df.columns]
        audit_table = audit_df[show_cols].rename(columns={
            "duplicate_group_id": "ID Grup Duplikasi",
            "tanggal": "Tanggal",
            "stasiun": "Stasiun",
            "max": "Max",
            "critical": "Critical",
            "categori": "Kategori",
            "duplicate_type": "Jenis Duplikasi",
            "dedup_action": "Tindakan Dedup",
            "used_for_main_dashboard_kpi": "Dipakai KPI Utama",
        })
        render_light_table(
            audit_table,
            numeric_cols=["Max"],
            chip_cols=["Critical", "Kategori", "Jenis Duplikasi", "Tindakan Dedup", "Dipakai KPI Utama"],
            long_cols=["Stasiun", "Jenis Duplikasi", "Tindakan Dedup"],
            max_height=560,
            max_rows=500,
        )
        st.download_button(
            label="Unduh audit duplikasi lengkap",
            data=audit_df.to_csv(index=False).encode("utf-8"),
            file_name="Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv",
            mime="text/csv",
            use_container_width=True,
        )

    section_title("Batasan interpretasi untuk pimpinan")
    st.markdown(
        '<div class="warning-panel"><p><b>Keputusan operasional harian tetap membutuhkan data terbaru atau real-time.</b> Dashboard ini kuat untuk membaca pola historis, prioritas risiko, lokasi, pencemar dominan, dan periode rawan berdasarkan clean dataset final. Data historis panjang tidak otomatis menggambarkan kondisi udara hari ini; karena itu tampilan default menggunakan tahun terakhir tersedia.</p></div>'
        '<div class="warning-panel"><p><b>Nilai max adalah indeks ISPU, bukan konsentrasi polutan mentah.</b> Critical menunjukkan parameter pembentuk indeks tertinggi pada observasi tersebut. Pada kasus multi-critical, beberapa parameter dapat memiliki nilai indeks tertinggi yang sama sehingga interpretasi pencemar dominan perlu berhati-hati.</p></div>'
        '<div class="warning-panel"><p><b>Dashboard ini bersifat deskriptif-diagnostik, bukan prediktif.</b> Untuk prediksi kualitas udara diperlukan model tambahan dengan variabel meteorologi, emisi, lalu lintas, aktivitas industri, dan validasi lapangan.</p></div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# MAIN
# =============================================================================


def main() -> None:
    try:
        clean_df, log_df, audit_df, validation_df = load_all_data()
    except Exception as exc:
        st.error("Dashboard belum dapat memuat data. Periksa struktur file CSV, nama kolom, dan folder data/ pada deployment Streamlit.")
        st.exception(exc)
        return

    if clean_df.empty:
        st.error(
            "Clean dataset final tidak ditemukan. Pastikan file CSV berada di folder data/ dengan nama "
            f"{DATA_FILES['clean']}"
        )
        return

    schema_notes = clean_df.attrs.get("schema_notes", [])
    if schema_notes:
        with st.expander("Catatan schema data", expanded=False):
            for note in schema_notes:
                st.warning(note)

    page, filtered_df, filters = build_sidebar(clean_df)
    hero(page, clean_df, filtered_df)

    if page == "Overview Kualitas Udara":
        page_overview(filtered_df, clean_df)
    elif page == "Tren Temporal":
        page_trend(filtered_df, clean_df)
    elif page == "Perbandingan Stasiun":
        page_station(filtered_df, clean_df)
    elif page == "Pencemar Kritis":
        page_critical(filtered_df, clean_df)
    elif page == "Pola Musiman":
        page_seasonal(filtered_df, clean_df)
    elif page == "Data Quality / Audit Trail":
        page_data_quality(filtered_df, clean_df, log_df, audit_df, validation_df)

    st.markdown("---")
    st.caption(
        "Dashboard BI ISPU DKI Jakarta · Color Contrast Decision Observatory: spektrum kualitas udara, unit observasi tanggal-stasiun, dan data historis untuk keputusan berbasis data."
    )


if __name__ == "__main__":
    main()
