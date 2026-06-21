"""Tape Up Media — Agency CRM Dashboard."""

import json
import os
import random
from datetime import datetime, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────
BRAND_PRIMARY  = "#8A2BE2"   # Premium Purple
BRAND_LIGHT    = "#a855f7"   # lighter purple for hover/line
BG_MAIN        = "#0a0a0a"   # Charcoal
BG_CARD        = "#111111"
BG_SIDEBAR     = "#0d0d0d"
BG_INPUT       = "#1a1a1a"
BORDER         = "#222222"
BORDER_ACCENT  = "#8A2BE2"
TEXT_DIM       = "#666666"
TEXT_MID       = "#999999"
TEXT_LIGHT     = "#e2e8f0"
GREEN          = "#22c55e"
RED            = "#ef4444"

PLATFORM_COLORS = {"instagram": BRAND_PRIMARY, "tiktok": BRAND_LIGHT}

PLOTLY_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=TEXT_MID,
    font_family="'Heebo', 'Arial Hebrew', sans-serif",
    legend=dict(
        orientation="h",
        yanchor="top",
        y=-0.2,
        xanchor="center",
        x=0.5,
        font=dict(color=TEXT_LIGHT),
        bgcolor="rgba(0,0,0,0)",
    ),
)

CHART_CONFIG = {"displayModeBar": False}

CLIENTS_FILE = os.path.join(os.path.dirname(__file__), "clients.json")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tape Up Media CRM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Heebo', 'Arial Hebrew', sans-serif !important;
    direction: rtl;
    box-sizing: border-box;
}}

/* Plotly SVG must stay LTR — RTL breaks label rendering */
.js-plotly-plot, .js-plotly-plot * {{
    direction: ltr !important;
}}

/* Dataframe iframe must stay LTR — RTL clips cell text to single chars */
.stDataFrame, .stDataFrame * {{
    direction: ltr !important;
}}

.stApp {{ background-color: {BG_MAIN}; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background-color: {BG_SIDEBAR} !important;
    border-left: 1px solid {BORDER};
    border-right: none;
}}
section[data-testid="stSidebar"] > div {{ direction: rtl; padding-top: 2rem; }}

/* ── Sidebar nav buttons ── */
div[data-testid="stSidebar"] .stButton > button {{
    width: 100%;
    text-align: right;
    background: transparent;
    border: none;
    border-radius: 10px;
    color: {TEXT_MID};
    font-size: 0.95rem;
    font-weight: 500;
    padding: 10px 16px;
    margin-bottom: 4px;
    transition: all 0.2s;
}}
div[data-testid="stSidebar"] .stButton > button:hover {{
    background: #1a1a1a;
    color: {TEXT_LIGHT};
}}

/* ── KPI metric cards ── */
div[data-testid="metric-container"] {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-top: 3px solid {BRAND_PRIMARY};
    border-radius: 14px;
    padding: 20px 24px;
    text-align: right;
}}
div[data-testid="metric-container"] label {{
    color: {TEXT_DIM} !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{
    color: #ffffff !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    direction: ltr;
    text-align: right;
}}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] > div {{
    color: {GREEN} !important;
    direction: ltr;
    text-align: right;
}}

/* ── Headings ── */
h1, h2, h3, h4 {{
    color: #ffffff !important;
    text-align: right;
    font-weight: 700;
}}
h1 {{ font-size: 1.9rem !important; letter-spacing: -0.02em; }}
h3 {{ font-size: 1.1rem !important; color: {TEXT_LIGHT} !important; margin-bottom: 14px; }}

/* ── Paragraphs ── */
p {{ color: {TEXT_LIGHT}; text-align: right; }}

/* ── Inputs & forms ── */
.stTextInput > div > div > input, .stSelectbox > div > div {{
    background-color: {BG_INPUT} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    color: {TEXT_LIGHT} !important;
    text-align: right;
    direction: rtl;
}}
.stTextInput > label, .stSelectbox > label {{
    color: {TEXT_DIM} !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}

/* ── Submit button ── */
div.stForm .stButton > button, div[data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(135deg, {BRAND_PRIMARY}, {BRAND_LIGHT});
    color: white;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 0.95rem;
    padding: 10px 28px;
    width: 100%;
    transition: opacity 0.2s;
}}
div.stForm .stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
    opacity: 0.85;
}}

/* ── Delete buttons ── */
.delete-btn button {{
    background: transparent !important;
    border: 1px solid {BORDER} !important;
    color: {RED} !important;
    border-radius: 8px !important;
    font-size: 0.8rem !important;
    padding: 4px 14px !important;
}}
.delete-btn button:hover {{ border-color: {RED} !important; background: #1a0a0a !important; }}

/* ── Section divider ── */
hr {{ border-color: {BORDER}; margin: 1.5rem 0; }}

/* ── Cards / panels ── */
.card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 22px 26px;
    margin-bottom: 12px;
}}

/* ── Insight box ── */
.insight-box {{
    background: linear-gradient(135deg, #0f0a1a, #110d1f);
    border: 1px solid #2a1a4a;
    border-right: 4px solid {BRAND_PRIMARY};
    border-radius: 14px;
    padding: 22px 26px;
    direction: rtl;
    text-align: right;
    margin: 4px 0 20px 0;
}}
.insight-box .insight-title {{
    color: {BRAND_LIGHT};
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    font-weight: 700;
    margin-bottom: 14px;
}}
.insight-box .insight-body {{
    color: {TEXT_LIGHT};
    font-size: 0.95rem;
    line-height: 2;
}}
.insight-box strong {{ color: #ffffff; }}

/* ── Client row card ── */
.client-row {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 12px;
    padding: 14px 20px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    direction: rtl;
}}
.client-name {{ color: #fff; font-weight: 700; font-size: 1rem; }}
.client-meta {{ color: {TEXT_DIM}; font-size: 0.82rem; margin-top: 2px; }}
.platform-tag {{
    display: inline-block;
    background: #1a0d2e;
    border: 1px solid {BRAND_PRIMARY}55;
    color: {BRAND_LIGHT};
    border-radius: 6px;
    padding: 2px 10px;
    font-size: 0.75rem;
    margin-right: 6px;
    direction: ltr;
}}

/* ── Brand badge ── */
.brand-badge {{ direction: ltr; text-align: left; }}
.brand-badge .en {{
    color: {BRAND_PRIMARY};
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.01em;
}}
.brand-badge .he {{
    color: {TEXT_DIM};
    font-size: 0.82rem;
    margin-right: 6px;
}}

/* ── Multiselect ── */
.stMultiSelect label {{ color: {TEXT_DIM} !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase; }}
.stMultiSelect > div {{ direction: rtl; }}

/* ── Dataframe ── */
.stDataFrame {{ border-radius: 12px; overflow: hidden; }}

/* ── Bug fix 4: hide Streamlit chrome ── */
#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ display: none; }}
.stDeployButton {{ display: none; }}
div[data-testid="stDecoration"] {{ display: none; }}

/* ── Success / error messages ── */
.stSuccess, .stError {{ border-radius: 10px; direction: rtl; text-align: right; }}
</style>
""", unsafe_allow_html=True)


# ── Client persistence ─────────────────────────────────────────────────────────
def load_clients() -> list[dict]:
    if not os.path.exists(CLIENTS_FILE):
        return []
    with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_clients(clients: list[dict]) -> None:
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)


# ── Mock data generation from clients.json ────────────────────────────────────
@st.cache_data(ttl=60)
def generate_data(client_names_key: str) -> pd.DataFrame:
    """Generate mock data for the current client list."""
    names = json.loads(client_names_key)
    if not names:
        return pd.DataFrame()
    random.seed(42)
    rows = []
    for client in names:
        for platform in ["instagram", "tiktok"]:
            for i in range(12):
                date = (datetime.now() - timedelta(days=i * 3)).strftime("%Y-%m-%d")
                rows.append({
                    "client":   client,
                    "platform": platform,
                    "date":     date,
                    "views":    random.randint(10_000, 500_000),
                    "likes":    random.randint(500, 20_000),
                    "comments": random.randint(50, 3_000),
                    "video_id": f"{platform[:2].upper()}-{random.randint(10000,99999)}",
                })
    return pd.DataFrame(rows)


# ── Session state ─────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "dashboard"


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style='text-align:center;padding:0 0 24px 0;'>
        <div style='font-size:1.5rem;margin-bottom:4px;'>📊</div>
        <div class='brand-badge' style='text-align:center;'>
            <span class='en'>Tape Up Media</span><br>
            <span class='he'>טייפ אפ מדיה</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p style='color:{TEXT_DIM};font-size:0.7rem;text-align:right;letter-spacing:0.08em;text-transform:uppercase;margin-bottom:8px;'>ניווט</p>", unsafe_allow_html=True)

    if st.button("📊  לוח בקרה", key="nav_dash"):
        st.session_state.page = "dashboard"
    if st.button("👥  ניהול לקוחות", key="nav_clients"):
        st.session_state.page = "clients"

    st.markdown("---")

    clients_list = load_clients()
    st.markdown(f"<p style='color:{TEXT_DIM};font-size:0.75rem;text-align:right;'>סה״כ לקוחות: <strong style='color:{TEXT_LIGHT};'>{len(clients_list)}</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_DIM};font-size:0.75rem;text-align:right;'>עדכון אחרון: {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":

    clients_list = load_clients()
    client_names = [c["name"] for c in clients_list]
    names_key    = json.dumps(client_names)
    df           = generate_data(names_key)

    # ── Header ────────────────────────────────────────────────────────────────
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown("# 📊 לוח בקרה — ביצועי וידאו")
        st.markdown(f"<p style='color:{TEXT_DIM};margin-top:-12px;'>סקירת נתוני צפיות לכל הלקוחות</p>", unsafe_allow_html=True)
    with col_badge:
        st.markdown(f"""
        <div class='brand-badge' style='padding-top:20px;text-align:left;'>
            <span class='en'>Tape Up Media</span>
            <span class='he'> — טייפ אפ מדיה</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    if df.empty:
        st.info("אין לקוחות במערכת. עבור לדף ניהול לקוחות כדי להוסיף.")
        st.stop()

    # ── Filters ───────────────────────────────────────────────────────────────
    fc1, fc2 = st.columns(2)
    with fc1:
        selected_clients = st.multiselect("לקוחות", client_names, default=client_names)
    with fc2:
        selected_platforms = st.multiselect("פלטפורמות", ["instagram", "tiktok"], default=["instagram", "tiktok"])

    filtered = df[
        df["client"].isin(selected_clients) &
        df["platform"].isin(selected_platforms)
    ]

    st.markdown("&nbsp;")

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_views    = filtered["views"].sum()
    total_likes    = filtered["likes"].sum()
    total_comments = filtered["comments"].sum()
    engagement     = ((total_likes + total_comments) / total_views * 100) if total_views else 0

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("סה״כ צפיות",    f"{total_views/1_000_000:.2f}M",  "+12.4%")
    k2.metric("סה״כ לייקים",   f"{total_likes/1_000:.1f}K",      "+8.1%")
    k3.metric("סה״כ תגובות",   f"{total_comments/1_000:.1f}K",   "+5.3%")
    k4.metric("ממוצע מעורבות", f"{engagement:.2f}%",             "+0.4%")

    st.markdown("&nbsp;")

    # ── AI Insights ───────────────────────────────────────────────────────────
    st.markdown("### 🧠 תובנות המערכת")

    tt_views = filtered[filtered["platform"] == "tiktok"]["views"].sum()
    ig_views = filtered[filtered["platform"] == "instagram"]["views"].sum()
    top_client = filtered.groupby("client")["views"].sum().idxmax() if not filtered.empty else "—"
    top_views_k = filtered[filtered["client"] == top_client]["views"].sum() / 1000

    better   = "טיקטוק" if tt_views > ig_views else "אינסטגרם"
    worse    = "אינסטגרם" if tt_views > ig_views else "טיקטוק"
    pct_diff = abs(tt_views - ig_views) / max(ig_views, tt_views, 1) * 100

    st.markdown(f"""
    <div class='insight-box'>
        <div class='insight-title'>⚡ תובנות אוטומטיות — מופעל על ידי AI</div>
        <div class='insight-body'>
            📈 <strong>{better}</strong> מציג ביצועים טובים יותר מ{worse} ב־<strong>{pct_diff:.0f}%</strong> החודש — מומלץ להגביר את קצב ההעלאות לפלטפורמה זו.<br>
            🏆 הלקוח המוביל הוא <strong>{top_client}</strong> עם <strong>{top_views_k:,.0f}K</strong> צפיות — כדאי לנתח את התוכן שעובד עבורו וליישם אצל לקוחות נוספים.<br>
            💡 שיעור המעורבות עומד על <strong>{engagement:.2f}%</strong> — סרטונים קצרים מתחת ל-30 שניות מציגים מעורבות גבוהה ב-40% בממוצע.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Charts row 1 ──────────────────────────────────────────────────────────
    c1, c2 = st.columns([2, 1])

    with c1:
        st.markdown("### צפיות לאורך זמן")
        time_df = (
            filtered.groupby(["date", "platform"])["views"]
            .sum().reset_index().sort_values("date")
        )
        fig_line = px.line(
            time_df, x="date", y="views", color="platform",
            color_discrete_map=PLATFORM_COLORS, markers=True,
            labels={"date": "תאריך", "views": "צפיות", "platform": "פלטפורמה"},
        )
        fig_line.update_layout(
            **PLOTLY_THEME,
            margin=dict(l=60, r=20, t=20, b=60),
            height=320,
            xaxis=dict(tickfont=dict(color=TEXT_MID), gridcolor="#1f1f1f"),
            yaxis=dict(tickfont=dict(color=TEXT_LIGHT, size=11), gridcolor="#1f1f1f", tickformat=".2s"),
        )
        fig_line.update_traces(line_width=2.5)
        st.plotly_chart(fig_line, use_container_width=True, config=CHART_CONFIG)

    with c2:
        st.markdown("### פיצול פלטפורמות")
        plat_df = filtered.groupby("platform")["views"].sum().reset_index()
        fig_pie = px.pie(
            plat_df, names="platform", values="views",
            color="platform", color_discrete_map=PLATFORM_COLORS, hole=0.62,
            labels={"platform": "פלטפורמה", "views": "צפיות"},
        )
        fig_pie.update_layout(**PLOTLY_THEME, margin=dict(l=0,r=0,t=20,b=60), height=320)
        fig_pie.update_traces(textinfo="percent", textfont_color="#fff")
        st.plotly_chart(fig_pie, use_container_width=True, config=CHART_CONFIG)

    # ── Charts row 2 ──────────────────────────────────────────────────────────
    st.markdown("### צפיות לפי לקוח")
    client_df = (
        filtered.groupby(["client", "platform"])["views"]
        .sum().reset_index().sort_values("views", ascending=True)
    )
    fig_bar = px.bar(
        client_df, x="views", y="client", color="platform",
        orientation="h", barmode="group",
        color_discrete_map=PLATFORM_COLORS,
        labels={"views": "צפיות", "client": "לקוח", "platform": "פלטפורמה"},
        text_auto=".2s",
    )
    fig_bar.update_traces(textposition="outside", textfont=dict(color=TEXT_LIGHT, size=11))
    fig_bar.update_layout(
        **PLOTLY_THEME,
        margin=dict(l=120, r=40, t=20, b=60),
        height=320,
        xaxis=dict(tickfont=dict(color=TEXT_MID), gridcolor="#1f1f1f"),
        yaxis=dict(tickfont=dict(color=TEXT_LIGHT, size=12), automargin=True),
        uniformtext_minsize=9,
        uniformtext_mode="hide",
    )
    st.plotly_chart(fig_bar, use_container_width=True, config=CHART_CONFIG)

    # ── Top videos table ──────────────────────────────────────────────────────
    st.markdown("### סרטונים מובילים")
    top = (
        filtered[["client","platform","date","video_id","views","likes","comments"]]
        .sort_values("views", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    st.dataframe(top, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CLIENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "clients":

    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown("# 👥 ניהול לקוחות")
        st.markdown(f"<p style='color:{TEXT_DIM};margin-top:-12px;'>הוספה, צפייה ומחיקה של לקוחות</p>", unsafe_allow_html=True)
    with col_badge:
        st.markdown(f"""
        <div class='brand-badge' style='padding-top:20px;text-align:left;'>
            <span class='en'>Tape Up Media</span>
            <span class='he'> — טייפ אפ מדיה</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Add client form ───────────────────────────────────────────────────────
    st.markdown("### ➕ הוספת לקוח חדש")

    with st.form("add_client_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            new_name = st.text_input("שם לקוח", placeholder="לדוג׳: Brand Alpha")
        with f2:
            new_ig = st.text_input("חשבון אינסטגרם", placeholder="@username")
        with f3:
            new_tt = st.text_input("חשבון טיקטוק", placeholder="@username")

        submitted = st.form_submit_button("✚  הוסף לקוח")

        if submitted:
            if not new_name.strip():
                st.error("שם הלקוח הוא שדה חובה.")
            else:
                clients = load_clients()
                existing_names = [c["name"].lower() for c in clients]
                if new_name.strip().lower() in existing_names:
                    st.error(f"לקוח בשם '{new_name}' כבר קיים במערכת.")
                else:
                    clients.append({
                        "name":      new_name.strip(),
                        "instagram": new_ig.strip(),
                        "tiktok":    new_tt.strip(),
                    })
                    save_clients(clients)
                    st.success(f"✅  הלקוח '{new_name}' נוסף בהצלחה!")
                    st.cache_data.clear()
                    st.rerun()

    st.markdown("&nbsp;")

    # ── Client list ───────────────────────────────────────────────────────────
    clients = load_clients()
    st.markdown(f"### רשימת לקוחות ({len(clients)})")

    if not clients:
        st.markdown(f"<div class='card'><p style='color:{TEXT_DIM};text-align:center;'>אין לקוחות. הוסף לקוח ראשון למעלה.</p></div>", unsafe_allow_html=True)
    else:
        for i, client in enumerate(clients):
            col_info, col_btn = st.columns([5, 1])

            with col_info:
                ig_tag = f"<span class='platform-tag'>📸 {client.get('instagram','—')}</span>" if client.get("instagram") else ""
                tt_tag = f"<span class='platform-tag'>🎵 {client.get('tiktok','—')}</span>"   if client.get("tiktok")    else ""
                st.markdown(f"""
                <div class='card' style='margin-bottom:0;'>
                    <div class='client-name'>{client['name']}</div>
                    <div class='client-meta' style='margin-top:6px;'>{ig_tag}{tt_tag}</div>
                </div>
                """, unsafe_allow_html=True)

            with col_btn:
                st.markdown("<div class='delete-btn'>", unsafe_allow_html=True)
                if st.button("🗑 מחק", key=f"del_{i}"):
                    clients.pop(i)
                    save_clients(clients)
                    st.cache_data.clear()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
