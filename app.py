"""
Dashboard BI ISPU DKI Jakarta
Tugas 6 - Business Intelligence Dashboard

Run:
    streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path
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


PAGE_PURPOSE = {
    "Overview Kualitas Udara": "Kondisi terkini dan prioritas cepat untuk keputusan pimpinan.",
    "Tren Temporal": "Arah perubahan kualitas udara dan periode yang melewati ambang risiko.",
    "Perbandingan Stasiun": "Lokasi prioritas pengendalian berdasarkan frekuensi risiko.",
    "Pencemar Kritis": "Parameter pencemar yang paling perlu dikendalikan.",
    "Pola Musiman": "Kalender antisipasi periode rawan kualitas udara.",
    "Data Quality / Audit Trail": "Kepercayaan data, batasan interpretasi, dan jejak validasi.",
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

.pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 0 0; }
.pill { display: inline-flex; align-items: center; padding: 7px 10px; border-radius: 999px; background: #FFFFFF; border: 1px solid var(--line); color: var(--slate) !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: .69rem; font-weight: 800; box-shadow: 0 8px 18px rgba(15,23,42,.05); }
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
button[data-baseweb="tab"] { font-weight: 800 !important; color: var(--slate) !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: var(--ink) !important; }
.streamlit-expanderHeader { font-weight: 800 !important; color: var(--ink) !important; }

.decision-grid { position: relative; z-index: 2; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 9px; margin-top: 11px; }
.decision-tile { border-radius: 16px; padding: 10px 12px; background: #FFFFFF; border: 1px solid var(--line); box-shadow: var(--shadow-soft); }
.decision-tile:nth-child(1) { background: linear-gradient(135deg, #FFFFFF, #EAF6FF); }
.decision-tile:nth-child(2) { background: linear-gradient(135deg, #FFFFFF, #FFF1E8); }
.decision-tile:nth-child(3) { background: linear-gradient(135deg, #FFFFFF, #ECFDF5); }
.decision-tile:nth-child(4) { background: linear-gradient(135deg, #FFFFFF, #F3EEFF); }
.decision-tile .tile-label { font-family: 'JetBrains Mono', ui-monospace, monospace; font-size: .66rem; letter-spacing: .10em; text-transform: uppercase; color: var(--muted) !important; font-weight: 800; }
.decision-tile .tile-value { margin-top: 5px; font-family: 'Barlow Condensed', 'Inter', sans-serif; font-weight: 800; font-size: 1.18rem; line-height: .98; color: var(--ink) !important; }
.air-ribbon-wrap { position: relative; z-index: 2; margin-top: 10px; border-radius: 16px; padding: 9px 11px; background: #FFFFFF; border: 1px solid var(--line); box-shadow: 0 8px 20px rgba(15,23,42,.055); }
.air-ribbon-title { display: flex; justify-content: space-between; gap: 12px; color: var(--slate) !important; font-family: 'JetBrains Mono', ui-monospace, monospace; font-weight: 800; font-size: .67rem; text-transform: uppercase; letter-spacing: .08em; margin-bottom: 8px; }
.air-ribbon { display: flex; width: 100%; overflow: hidden; height: 13px; border-radius: 999px; border: 1px solid rgba(15,23,42,.16); background: #FFFFFF; }
.air-ribbon-segment { height: 100%; min-width: 1.2%; }
.air-ribbon-legend { display: flex; flex-wrap: wrap; gap: 7px 12px; margin-top: 8px; color: var(--slate) !important; font-size: .69rem; font-weight: 800; }
.legend-dot { display: inline-flex; align-items: center; gap: 6px; color: var(--slate) !important; }
.legend-dot::before { content:""; width: 9px; height: 9px; border-radius: 999px; background: var(--dot); box-shadow: 0 0 0 3px rgba(15,23,42,.06); }
.page-brief { border-radius: 22px; padding: 14px 16px; margin: 1rem 0 .65rem 0; background: #FFFFFF; border: 1px solid var(--line); color: var(--slate) !important; box-shadow: var(--shadow-soft); }
.page-brief b { color: var(--ink) !important; }
[data-testid="stPlotlyChart"] { border: 1px solid var(--line); border-radius: 24px; padding: 10px 10px 2px 10px; background: #FFFFFF; box-shadow: var(--shadow-soft), inset 0 1px 0 rgba(255,255,255,.88); }
.sidebar-purpose { margin: 8px 0 4px 0; border-radius: 18px; padding: 12px 13px; background: linear-gradient(135deg, #EAF6FF, #FFFFFF); border: 1px solid rgba(2,132,199,.22); color: var(--slate) !important; font-size: .82rem; line-height: 1.45; font-weight: 600; }
.empty-state-panel { border-radius: 24px; padding: 22px; border: 1px dashed rgba(225,29,72,.42); background: #FFFFFF; color: var(--ink) !important; box-shadow: var(--shadow-soft); }
.empty-state-panel * { color: var(--ink) !important; }

/* Readability hardening: anything inside custom panels must stay dark, never pastel-on-pastel. */
.command-hero *, .kpi-card *, .glass-panel *, .insight-panel *, .warning-panel *, .decision-tile *, .air-ribbon-wrap *, .page-brief *, .sidebar-purpose * { text-shadow: none !important; }

@media (max-width: 980px) {
    .hero-grid { grid-template-columns: 1fr; }
    .hero-meta { min-width: unset; }
    .command-hero { padding: 24px 22px; border-radius: 26px; }
    .decision-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 620px) { .decision-grid { grid-template-columns: 1fr; } }
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


def kpi_card(label: str, value: str, delta: str = "", note: str = "", accent: str = "#00A676") -> None:
    delta_html = f'<div class="kpi-delta">{delta}</div>' if delta else ""
    note_html = f'<div class="kpi-note">{note}</div>' if note else ""
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{accent};">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(title: str) -> None:
    st.markdown(
        f"""
        <div class="section-title">
            <div class="bar"></div>
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )




def page_brief(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="page-brief"><b>{title}</b><br>{body}</div>
        """,
        unsafe_allow_html=True,
    )


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
        if width > 0:
            segments.append(f'<div class="air-ribbon-segment" title="{cat}: {pct:.1f}%" style="width:{width:.3f}%; background:{color};"></div>')
        legends.append(f'<span class="legend-dot" style="--dot:{color};">{cat}: {pct:.1f}%</span>')
    return f"""
    <div class="air-ribbon-wrap">
        <div class="air-ribbon-title"><span>Spektrum kategori ISPU pada filter aktif</span><span>Baik → Berbahaya</span></div>
        <div class="air-ribbon">{"".join(segments)}</div>
        <div class="air-ribbon-legend">{"".join(legends)}</div>
    </div>
    """


def insight_panel(title: str, body: str, kind: str = "insight") -> None:
    class_name = "warning-panel" if kind == "warning" else "insight-panel"
    if kind == "warning":
        st.markdown(f'<div class="{class_name}"><p>{body}</p></div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f"""
            <div class="{class_name}">
                <div class="insight-title">{title}</div>
                <p>{body}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def apply_fig_style(fig: go.Figure, height: Optional[int] = None, legend: bool = True) -> go.Figure:
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Arial, sans-serif", color="#102033", size=12),
        title_font=dict(family="Barlow Condensed, Inter, sans-serif", color="#102033", size=20),
        margin=dict(t=52, r=24, b=42, l=32),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor="rgba(15,23,42,.22)", font_color="#102033"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#334155"),
        ) if legend else dict(visible=False),
    )
    if height:
        fig.update_layout(height=height)
    fig.update_xaxes(
        showgrid=False,
        linecolor="rgba(15,23,42,.20)",
        tickfont=dict(color="#334155"),
        title_font=dict(color="#334155"),
    )
    fig.update_yaxes(
        gridcolor="rgba(15,23,42,.10)",
        zerolinecolor="rgba(15,23,42,.14)",
        tickfont=dict(color="#334155"),
        title_font=dict(color="#334155"),
    )
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


def download_filtered_data(df: pd.DataFrame, filename: str) -> None:
    st.download_button(
        label="Unduh data terfilter",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )


def hero(current_page: str, df: pd.DataFrame, filtered: pd.DataFrame) -> None:
    if df.empty:
        period = "Data belum tersedia"
        status = "Perlu unggah data"
        data_end = "—"
    else:
        start = df["tanggal_clean"].min().strftime("%d %b %Y")
        end = df["tanggal_clean"].max().strftime("%d %b %Y")
        latest = latest_year(df)
        period = f"{start} – {end} · fokus default: {latest}"
        status = "Clean dataset final"
        data_end = end

    if filtered.empty:
        avg_ispu = np.nan
        unhealthy = np.nan
        top_station_code = "—"
        top_critical = "—"
        filtered_hint = "Tidak ada observasi aktif"
    else:
        avg_ispu = filtered["max"].mean()
        unhealthy = pct_true(filtered["flag_tidak_sehat_plus"])
        st_summary = station_summary(filtered)
        top_station_code = station_code(st_summary.iloc[0]["stasiun"]) if not st_summary.empty else "—"
        top_critical = mode_or_dash(filtered["critical"])
        filtered_hint = f"{fmt_int(len(filtered))} observasi tanggal-stasiun aktif"

    status_cat = ispu_status_from_average(avg_ispu)
    page_purpose = PAGE_PURPOSE.get(current_page, "")

    st.markdown(
        f"""
        <div class="command-hero" aria-label="Observatorium kualitas udara Jakarta dengan nuansa langit senja pastel">
            <div class="hero-grid">
                <div>
                    <div class="hero-eyebrow">Kualitas Udara DKI Jakarta · {current_page}</div>
                    <h1 class="hero-title">{APP_TITLE}</h1>
                    <div class="hero-copy">{APP_SUBTITLE}</div>
                    <div class="pill-row">
                        <div class="pill">Ambang keputusan: ISPU 101</div>
                        <div class="pill">Metrik utama: % observasi Tidak Sehat+</div>
                        <div class="pill">Unit: tanggal-stasiun</div>
                        <div class="pill">Data historis, bukan real-time</div>
                        <div class="pill">{filtered_hint}</div>
                    </div>
                </div>
                <div class="hero-meta">
                    <div class="label">Periode data</div>
                    <div class="value">{period}</div>
                    <div class="status">{status}</div>
                    <div class="data-badge">Data historis · bukan status udara real-time</div>
                </div>
            </div>
            <div class="decision-grid">
                <div class="decision-tile"><div class="tile-label">Status rata-rata</div><div class="tile-value">{status_cat}</div></div>
                <div class="decision-tile"><div class="tile-label">Tidak Sehat+</div><div class="tile-value">{fmt_pct(unhealthy, 1)}</div></div>
                <div class="decision-tile"><div class="tile-label">Prioritas lokasi</div><div class="tile-value">{top_station_code}</div></div>
                <div class="decision-tile"><div class="tile-label">Pencemar dominan</div><div class="tile-value">{top_critical}</div></div>
            </div>
            {air_quality_ribbon(filtered)}
        </div>
        """,
        unsafe_allow_html=True,
    )
    page_brief("Fokus halaman", page_purpose + f" Data terakhir tersedia: {data_end}. Semua persentase dihitung dari unit observasi tanggal-stasiun pada filter aktif, kecuali dinyatakan lain.")


def empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state-panel">
            <b>Tidak ada data pada filter aktif.</b><br>
            Longgarkan rentang periode, pilih kembali stasiun, kategori, atau pencemar kritis. Dashboard tidak merender grafik kosong agar keputusan tidak dibaca dari basis data nol.
        </div>
        """,
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
    fig.update_yaxes(range=[0, max(10, yearly["persen_tidak_sehat_plus"].max() * 1.25)])
    return apply_fig_style(fig, height=410)


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
    return apply_fig_style(fig, height=430)


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
    return apply_fig_style(fig, height=500)


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
    return apply_fig_style(fig, height=430)


def fig_critical_trend_year(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby(["tahun", "critical"])
        .size()
        .reset_index(name="jumlah")
    )
    data["persentase"] = data["jumlah"] / data.groupby("tahun")["jumlah"].transform("sum") * 100
    fig = px.area(
        data,
        x="tahun",
        y="persentase",
        color="critical",
        color_discrete_map=CRITICAL_COLORS,
        title="Perubahan komposisi pencemar kritis per tahun",
        labels={"tahun": "Tahun", "persentase": "Persentase (%)", "critical": "Pencemar"},
        hover_data={"jumlah": True, "persentase": ":.1f"},
    )
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return apply_fig_style(fig, height=430)


def fig_critical_heatmap(df: pd.DataFrame) -> go.Figure:
    data = (
        df.groupby(["stasiun", "critical"])
        .size()
        .reset_index(name="jumlah")
    )
    data["kode"] = data["stasiun"].map(station_code)
    pivot = data.pivot_table(index="kode", columns="critical", values="jumlah", aggfunc="sum", fill_value=0)
    pivot = pivot.reindex(columns=[c for c in ["PM10", "PM25", "SO2", "CO", "O3", "NO2"] if c in pivot.columns] + [c for c in pivot.columns if c not in ["PM10", "PM25", "SO2", "CO", "O3", "NO2"]])
    fig = px.imshow(
        pivot,
        aspect="auto",
        color_continuous_scale=["#F8FAFC", "#BAE6FD", "#FDE68A", "#FDBA74", "#F43F5E"],
        title="Heatmap frekuensi pencemar kritis · stasiun × parameter",
        labels=dict(x="Pencemar", y="Stasiun", color="Jumlah"),
    )
    fig.update_traces(hovertemplate="Stasiun: %{y}<br>Pencemar: %{x}<br>Jumlah: %{z}<extra></extra>")
    return apply_fig_style(fig, height=430, legend=False)


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

    page_brief("Pertanyaan keputusan", "Seberapa serius kondisi udara pada periode aktif, di mana lokasi prioritas, dan pencemar apa yang perlu segera diperhatikan? Angka dihitung dari observasi tanggal-stasiun pada filter aktif.")

    avg_ispu = df["max"].mean()
    median_ispu = df["max"].median()
    unhealthy = pct_true(df["flag_tidak_sehat_plus"])
    top_category = mode_or_dash(df["categori"])
    top_critical = mode_or_dash(df["critical"])
    stations = station_summary(df)
    top_station = stations.iloc[0] if not stations.empty else None

    section_title("Napas Kota Terkini")
    c1, c2, c3, c4, c5 = st.columns(5)
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

    section_title("Komposisi risiko dan pencemar utama")
    left, right = st.columns([1.1, 1])
    with left:
        st.plotly_chart(fig_category_distribution(df), use_container_width=True)
    with right:
        st.plotly_chart(fig_critical_distribution(df), use_container_width=True)

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
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rata-rata ISPU": st.column_config.NumberColumn(format="%.1f"),
            "Median ISPU": st.column_config.NumberColumn(format="%.1f"),
            "% Tidak Sehat+": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
        },
    )

    top_station_name = top_station["stasiun"] if top_station is not None else "—"
    top_station_pct = top_station["persen_tidak_sehat_plus"] if top_station is not None else np.nan
    insight_panel(
        "Insight eksekutif",
        f"Pada periode terpilih, berdasarkan <b>{obs_context_active(df)}</b>, kondisi dominan adalah <b>{top_category}</b> dengan rata-rata ISPU <b>{fmt_float(avg_ispu, 1)}</b>. "
        f"Proporsi observasi <b>Tidak Sehat+</b> mencapai <b>{fmt_pct(unhealthy, 1)}</b>. "
        f"Stasiun yang perlu diprioritaskan adalah <b>{top_station_name}</b> dengan risiko Tidak Sehat+ sebesar <b>{fmt_pct(top_station_pct, 1)}</b> dari observasi tanggal-stasiun di stasiun tersebut. "
        f"Pencemar kritis yang paling sering muncul adalah <b>{top_critical}</b>.",
    )

    insight_panel(
        "Arahan tindakan",
        "Gunakan halaman ini sebagai ringkasan cepat untuk menetapkan prioritas awal: fokus pada stasiun dengan frekuensi Tidak Sehat+ tertinggi, lalu dalami pencemar dominan pada menu Pencemar Kritis dan periode rawan pada menu Pola Musiman.",
    )

    download_filtered_data(df, "ispu_jakarta_filtered_overview.csv")


def page_trend(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Pertanyaan keputusan", "Apakah kualitas udara sedang membaik, memburuk, atau fluktuatif; dan kapan nilai ISPU melewati ambang Tidak Sehat? Persentase risiko menggunakan observasi tanggal-stasiun sebagai denominator.")

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
    st.plotly_chart(fig_trend_line(df, granularity, view_mode, include_all_thresholds), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(fig_unhealthy_by_year(df), use_container_width=True)
    with right:
        st.plotly_chart(fig_category_by_year(df), use_container_width=True)

    trend_direction = "memburuk" if not pd.isna(delta_unhealthy) and delta_unhealthy > 0 else "membaik/menurun" if not pd.isna(delta_unhealthy) and delta_unhealthy < 0 else "relatif stabil atau belum dapat dibandingkan"
    insight_panel(
        "Insight tren",
        f"Pada tahun terakhir dalam filter ({max_year}), berdasarkan <b>{fmt_int(len(df[df['tahun'] == max_year]))} observasi tanggal-stasiun</b>, rata-rata ISPU sebesar <b>{fmt_float(cur_avg, 1)}</b> dan frekuensi Tidak Sehat+ sebesar <b>{fmt_pct(cur_unhealthy, 1)}</b>. "
        f"Dibanding tahun sebelumnya, perubahan frekuensi Tidak Sehat+ menunjukkan kondisi <b>{trend_direction}</b>. Garis threshold ISPU 101 membantu membaca periode ketika kualitas udara mulai masuk kategori Tidak Sehat.",
    )
    insight_panel(
        "Arahan tindakan",
        "Periode yang berulang melewati ambang Tidak Sehat perlu menjadi target evaluasi kebijakan, penguatan pemantauan, dan komunikasi risiko. Untuk keputusan operasional, baca tren tahun terakhir lebih dulu, lalu gunakan tren historis sebagai pembanding.",
    )


def page_station(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Pertanyaan keputusan", "Stasiun mana yang harus menjadi prioritas pengendalian pencemaran berdasarkan frekuensi risiko dan tekanan ISPU? Perbandingan memakai persentase per stasiun agar lebih adil.")

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

    section_title("Perbandingan risiko antar SPKU")
    left, right = st.columns([1, 1.05])
    with left:
        st.plotly_chart(fig_station_risk_bar(summary), use_container_width=True)
    with right:
        st.plotly_chart(fig_station_bubble(summary), use_container_width=True)

    section_title("Komposisi kategori per stasiun")
    st.plotly_chart(fig_station_category_stack(df), use_container_width=True)

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
    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rata-rata ISPU": st.column_config.NumberColumn(format="%.1f"),
            "% Tidak Sehat+": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
        },
    )

    insight_panel(
        "Insight lokasi",
        f"Stasiun <b>{top['stasiun']}</b> menjadi prioritas karena memiliki frekuensi Tidak Sehat+ tertinggi sebesar <b>{fmt_pct(top['persen_tidak_sehat_plus'], 1)}</b>. "
        f"Perbandingan ini memakai persentase dari observasi tanggal-stasiun pada masing-masing stasiun, bukan jumlah mentah, sehingga lebih adil ketika jumlah observasi antar stasiun berbeda. Filter aktif berisi <b>{obs_context(df)}</b>.",
    )
    insight_panel(
        "Arahan tindakan",
        "Prioritaskan pengawasan, evaluasi sumber emisi, dan validasi lapangan pada stasiun dengan status Prioritas Tinggi. Gunakan pencemar dominan per stasiun sebagai dasar untuk menentukan intervensi teknis yang lebih spesifik.",
    )


def page_critical(df: pd.DataFrame, full_df: pd.DataFrame) -> None:
    if df.empty:
        empty_state()
        return

    page_brief("Pertanyaan keputusan", "Parameter pencemar apa yang paling sering mendorong risiko kualitas udara dan perlu menjadi fokus pengendalian? Critical dibaca sebagai parameter pembentuk indeks tertinggi, bukan konsentrasi fisik terbesar.")

    crit_df = df[df["critical"].notna() & (df["critical"] != "TIDAK ADA DATA")].copy()
    if crit_df.empty:
        st.warning("Tidak ada data pencemar kritis yang tersedia pada filter aktif.")
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
        st.plotly_chart(fig_critical_distribution(crit_df, "Ranking pencemar kritis keseluruhan"), use_container_width=True)
    with right:
        st.plotly_chart(fig_critical_heatmap(crit_df), use_container_width=True)

    section_title("Pencemar kritis menurut lokasi dan waktu")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_critical_by_station(crit_df), use_container_width=True)
    with col2:
        st.plotly_chart(fig_critical_trend_year(crit_df), use_container_width=True)

    section_title("Pencemar pada kondisi Tidak Sehat+")
    if unhealthy_crit.empty:
        st.info("Tidak ada observasi Tidak Sehat+ pada filter aktif.")
    else:
        st.plotly_chart(fig_critical_distribution(unhealthy_crit, "Pencemar dominan khusus kategori Tidak Sehat+"), use_container_width=True)

    insight_panel(
        "Insight pencemar",
        f"Pencemar kritis paling dominan pada periode terpilih adalah <b>{top_crit}</b> dengan porsi <b>{fmt_pct(top_crit_pct, 1)}</b> dari <b>{fmt_int(len(crit_df))} observasi tanggal-stasiun yang memiliki critical</b>. "
        f"Pada observasi Tidak Sehat+, pencemar dominan adalah <b>{top_crit_unhealthy}</b>. Ini membantu mengarahkan kebijakan dari sekadar mengetahui udara buruk menjadi mengetahui parameter yang perlu dikendalikan.",
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

    page_brief("Pertanyaan keputusan", "Bulan apa yang menjadi periode rawan dan kapan Dinas perlu meningkatkan pemantauan serta komunikasi risiko? Pola musiman dibaca dari observasi tanggal-stasiun pada filter aktif.")

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
    st.plotly_chart(fig_seasonal_heatmap(df, metric), use_container_width=True)

    left, right = st.columns(2)
    with left:
        st.plotly_chart(fig_monthly_bars(df, "Rata-rata ISPU"), use_container_width=True)
    with right:
        st.plotly_chart(fig_monthly_bars(df, "% Tidak Sehat+"), use_container_width=True)

    section_title("Pola musiman per stasiun")
    st.plotly_chart(fig_monthly_station_line(df), use_container_width=True)

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
    st.dataframe(
        calendar[["Bulan", "Rata-rata ISPU", "% Tidak Sehat+", "Pencemar Dominan", "Status Operasional", "Arahan Operasional"]],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Rata-rata ISPU": st.column_config.NumberColumn(format="%.1f"),
            "% Tidak Sehat+": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, max_value=100),
        },
    )

    insight_panel(
        "Insight musiman",
        f"Berdasarkan <b>{obs_context_active(df)}</b>, bulan dengan rata-rata ISPU tertinggi adalah <b>{worst_avg['nama_bulan']}</b>, sedangkan bulan dengan frekuensi Tidak Sehat+ tertinggi adalah <b>{worst_risk['nama_bulan']}</b>. "
        f"Bulan rawan ini perlu dibaca sebagai kalender kewaspadaan agar tindakan tidak hanya reaktif ketika polusi sudah tinggi.",
    )
    insight_panel(
        "Arahan tindakan",
        "Gunakan bulan dengan status Prioritas Tinggi sebagai periode peningkatan pemantauan, inspeksi sumber emisi, validasi lapangan, dan komunikasi risiko kepada masyarakat. Untuk bulan risiko menengah, siapkan respons dini bila indikator mulai naik.",
    )


def page_data_quality(df: pd.DataFrame, full_df: pd.DataFrame, log_df: pd.DataFrame, audit_df: pd.DataFrame, validation_df: pd.DataFrame) -> None:
    if full_df.empty:
        empty_state()
        return

    page_brief("Pertanyaan keputusan", "Apakah data cukup valid, cukup terkini, dan cukup representatif untuk dijadikan dasar keputusan? Menu ini juga membatasi interpretasi agar dashboard tidak dibaca sebagai prediksi atau status real-time.")

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

    insight_panel(
        "Makna untuk pengambilan keputusan",
        "Menu ini memastikan angka pada dashboard tidak dibaca secara keliru. Dataset final sudah dibuat unik pada level tanggal-stasiun, hasil validasi akhir ditampilkan, dan data duplikasi dipisahkan ke audit agar tidak menggandakan KPI utama.",
    )

    section_title("Cakupan Sensor dan Periode")
    col1, col2 = st.columns(2)
    with col1:
        yearly = full_df.groupby("tahun").size().reset_index(name="observasi")
        fig = px.bar(yearly, x="tahun", y="observasi", title="Jumlah observasi per tahun", labels={"tahun": "Tahun", "observasi": "Observasi"})
        fig.update_traces(marker_color="#0284C7", text=yearly["observasi"], textposition="outside", cliponaxis=False)
        st.plotly_chart(apply_fig_style(fig, height=380, legend=False), use_container_width=True)
    with col2:
        station_cov = full_df.groupby("stasiun").size().reset_index(name="observasi")
        station_cov["kode"] = station_cov["stasiun"].map(station_code)
        fig = px.bar(station_cov.sort_values("observasi", ascending=True), x="observasi", y="kode", orientation="h", title="Jumlah observasi per stasiun", labels={"observasi": "Observasi", "kode": "Stasiun"}, hover_data={"stasiun": True})
        fig.update_traces(marker_color="#00A676", text="observasi", textposition="outside", cliponaxis=False)
        st.plotly_chart(apply_fig_style(fig, height=380, legend=False), use_container_width=True)

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
    st.plotly_chart(apply_fig_style(fig, height=420, legend=False), use_container_width=True)
    insight_panel(
        "Catatan batasan data",
        "Ketersediaan parameter tidak selalu sama sepanjang periode historis. Khusus PM2.5, interpretasi lintas tahun perlu mempertimbangkan periode kemunculan data agar Kepala Dinas tidak salah menyimpulkan dominasi atau absennya PM2.5 pada tahun awal.",
        kind="warning",
    )

    section_title("Hasil Validasi Akhir")
    if validation_df.empty:
        st.info("File validasi final tidak tersedia.")
    else:
        val = validation_df.copy()
        val["status"] = np.where(val["jumlah_baris_bermasalah"] == 0, "Aman", "Perlu perhatian")
        st.dataframe(
            val.rename(columns={"aspek_validasi": "Aspek Validasi", "jumlah_baris_bermasalah": "Jumlah Baris Bermasalah", "status": "Status"}),
            use_container_width=True,
            hide_index=True,
            column_config={"Jumlah Baris Bermasalah": st.column_config.NumberColumn(format="%d")},
        )

    section_title("Jejak Pembersihan Data")
    if log_df.empty:
        st.info("File cleaning log tidak tersedia.")
    else:
        show_cols = [c for c in ["tahap", "masalah", "kolom_terdampak", "jumlah_baris_terdampak", "strategi_penanganan", "justifikasi", "dampak_setelah_cleaning"] if c in log_df.columns]
        st.dataframe(log_df[show_cols], use_container_width=True, hide_index=True)

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
                st.plotly_chart(apply_fig_style(fig, height=360, legend=False), use_container_width=True)
        with col2:
            if "duplicate_type" in audit_df.columns:
                typ = audit_df.groupby("duplicate_type").size().reset_index(name="jumlah")
                fig = px.bar(typ, x="duplicate_type", y="jumlah", title="Jenis duplikasi", labels={"duplicate_type": "Jenis", "jumlah": "Jumlah"}, text="jumlah")
                fig.update_traces(marker_color="#F97316", textposition="outside", cliponaxis=False)
                st.plotly_chart(apply_fig_style(fig, height=360, legend=False), use_container_width=True)
        show_cols = [c for c in ["duplicate_group_id", "tanggal", "stasiun", "max", "critical", "categori", "duplicate_type", "dedup_action", "used_for_main_dashboard_kpi"] if c in audit_df.columns]
        st.dataframe(audit_df[show_cols].head(500), use_container_width=True, hide_index=True)
        st.download_button(
            label="Unduh audit duplikasi lengkap",
            data=audit_df.to_csv(index=False).encode("utf-8"),
            file_name="Audit_Duplikasi_Tanggal_Stasiun_ISPU_Jakarta_FINAL.csv",
            mime="text/csv",
            use_container_width=True,
        )

    section_title("Batasan interpretasi untuk pimpinan")
    st.markdown(
        """
        <div class="warning-panel">
            <p><b>Keputusan operasional harian tetap membutuhkan data terbaru atau real-time.</b> Dashboard ini kuat untuk membaca pola historis, prioritas risiko, lokasi, pencemar dominan, dan periode rawan berdasarkan clean dataset final. Data historis panjang tidak otomatis menggambarkan kondisi udara hari ini; karena itu tampilan default menggunakan tahun terakhir tersedia.</p>
        </div>
        <div class="warning-panel">
            <p><b>Nilai max adalah indeks ISPU, bukan konsentrasi polutan mentah.</b> Critical menunjukkan parameter pembentuk indeks tertinggi pada observasi tersebut. Pada kasus multi-critical, beberapa parameter dapat memiliki nilai indeks tertinggi yang sama sehingga interpretasi pencemar dominan perlu berhati-hati.</p>
        </div>
        <div class="warning-panel">
            <p><b>Dashboard ini bersifat deskriptif-diagnostik, bukan prediktif.</b> Untuk prediksi kualitas udara diperlukan model tambahan dengan variabel meteorologi, emisi, lalu lintas, aktivitas industri, dan validasi lapangan.</p>
        </div>
        """,
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
