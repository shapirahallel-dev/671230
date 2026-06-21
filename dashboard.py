"""Tape Up Media — Agency CRM Dashboard."""

import json
import os
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# ── Constants ─────────────────────────────────────────────────────────────────
BRAND_PRIMARY  = "#8A2BE2"
BRAND_LIGHT    = "#a855f7"
BG_MAIN        = "#0a0a0a"
BG_CARD        = "#111111"
BG_SIDEBAR     = "#0d0d0d"
BG_INPUT       = "#1a1a1a"
BORDER         = "#222222"
TEXT_DIM       = "#666666"
TEXT_MID       = "#999999"
TEXT_LIGHT     = "#e2e8f0"
GREEN          = "#22c55e"
RED            = "#ef4444"

PLATFORM_COLORS = {"instagram": BRAND_PRIMARY, "tiktok": BRAND_LIGHT}
CHART_CONFIG    = {"displayModeBar": False}
PLOTLY_THEME    = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color=TEXT_MID,
    font_family="'Heebo', 'Arial Hebrew', sans-serif",
    legend=dict(
        orientation="h", yanchor="top", y=-0.2,
        xanchor="center", x=0.5,
        font=dict(color=TEXT_LIGHT),
        bgcolor="rgba(0,0,0,0)",
    ),
)

BASE_DIR     = os.path.dirname(__file__)
CLIENTS_FILE = os.path.join(BASE_DIR, "clients.json")
METRICS_FILE = os.path.join(BASE_DIR, "metrics.json")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tape Up Media CRM",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700;800&display=swap');

*, html, body, [class*="css"] {{
    font-family: 'Heebo', 'Arial Hebrew', sans-serif !important;
    direction: rtl;
    box-sizing: border-box;
}}
.js-plotly-plot, .js-plotly-plot * {{ direction: ltr !important; }}
.stDataFrame, .stDataFrame * {{ direction: ltr !important; }}

.stApp {{ background-color: {BG_MAIN}; }}

section[data-testid="stSidebar"] {{
    background-color: {BG_SIDEBAR} !important;
    border-left: 1px solid {BORDER};
    border-right: none;
}}
section[data-testid="stSidebar"] > div {{ direction: rtl; padding-top: 2rem; }}

div[data-testid="stSidebar"] .stButton > button {{
    width: 100%; text-align: right; background: transparent; border: none;
    border-radius: 10px; color: {TEXT_MID}; font-size: 0.95rem; font-weight: 500;
    padding: 10px 16px; margin-bottom: 4px; transition: all 0.2s;
}}
div[data-testid="stSidebar"] .stButton > button:hover {{ background: #1a1a1a; color: {TEXT_LIGHT}; }}

div[data-testid="metric-container"] {{
    background: {BG_CARD}; border: 1px solid {BORDER};
    border-top: 3px solid {BRAND_PRIMARY}; border-radius: 14px; padding: 20px 24px; text-align: right;
}}
div[data-testid="metric-container"] label {{ color: {TEXT_DIM} !important; font-size: 0.75rem !important; font-weight: 600 !important; letter-spacing: 0.06em; text-transform: uppercase; }}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {{ color: #fff !important; font-size: 2rem !important; font-weight: 800 !important; direction: ltr; text-align: right; }}
div[data-testid="metric-container"] div[data-testid="stMetricDelta"] > div {{ color: {GREEN} !important; direction: ltr; text-align: right; }}

h1, h2, h3, h4 {{ color: #fff !important; text-align: right; font-weight: 700; }}
h1 {{ font-size: 1.9rem !important; letter-spacing: -0.02em; }}
h3 {{ font-size: 1.1rem !important; color: {TEXT_LIGHT} !important; margin-bottom: 14px; }}
p {{ color: {TEXT_LIGHT}; text-align: right; }}

.stTextInput > div > div > input, .stSelectbox > div > div {{
    background-color: {BG_INPUT} !important; border: 1px solid {BORDER} !important;
    border-radius: 10px !important; color: {TEXT_LIGHT} !important; direction: rtl;
}}
.stTextInput > label, .stSelectbox > label, .stNumberInput > label, .stDateInput > label, .stSelectbox label {{
    color: {TEXT_DIM} !important; font-size: 0.78rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.06em;
}}
div[data-testid="stFormSubmitButton"] > button {{
    background: linear-gradient(135deg, {BRAND_PRIMARY}, {BRAND_LIGHT});
    color: white; border: none; border-radius: 10px; font-weight: 700;
    font-size: 0.95rem; padding: 10px 28px; width: 100%; transition: opacity 0.2s;
}}
div[data-testid="stFormSubmitButton"] > button:hover {{ opacity: 0.85; }}

.delete-btn button {{
    background: transparent !important; border: 1px solid {BORDER} !important;
    color: {RED} !important; border-radius: 8px !important; font-size: 0.8rem !important; padding: 4px 14px !important;
}}
.delete-btn button:hover {{ border-color: {RED} !important; background: #1a0a0a !important; }}

hr {{ border-color: {BORDER}; margin: 1.5rem 0; }}
.card {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 14px; padding: 22px 26px; margin-bottom: 12px; }}

.insight-box {{
    background: linear-gradient(135deg, #0f0a1a, #110d1f);
    border: 1px solid #2a1a4a; border-right: 4px solid {BRAND_PRIMARY};
    border-radius: 14px; padding: 22px 26px; direction: rtl; text-align: right; margin: 4px 0 20px 0;
}}
.insight-box .insight-title {{ color: {BRAND_LIGHT}; font-size: 0.72rem; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 700; margin-bottom: 14px; }}
.insight-box .insight-body {{ color: {TEXT_LIGHT}; font-size: 0.95rem; line-height: 2; }}
.insight-box strong {{ color: #fff; }}

.platform-tag {{
    display: inline-block; background: #1a0d2e; border: 1px solid {BRAND_PRIMARY}55;
    color: {BRAND_LIGHT}; border-radius: 6px; padding: 2px 10px; font-size: 0.75rem; margin-right: 6px; direction: ltr;
}}
.brand-badge {{ direction: ltr; text-align: left; }}
.brand-badge .en {{ color: {BRAND_PRIMARY}; font-weight: 800; font-size: 1.05rem; }}
.brand-badge .he {{ color: {TEXT_DIM}; font-size: 0.82rem; margin-right: 6px; }}

.stMultiSelect label {{ color: {TEXT_DIM} !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase; }}
.stMultiSelect > div {{ direction: rtl; }}
.stDataFrame {{ border-radius: 12px; overflow: hidden; }}

#MainMenu {{ visibility: hidden; }}
footer {{ visibility: hidden; }}
header[data-testid="stHeader"] {{ display: none; }}
.stDeployButton {{ display: none; }}
div[data-testid="stDecoration"] {{ display: none; }}
</style>
""", unsafe_allow_html=True)


# ── Persistence helpers ───────────────────────────────────────────────────────
def load_clients() -> list[dict]:
    if not os.path.exists(CLIENTS_FILE):
        return []
    with open(CLIENTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_clients(clients: list[dict]) -> None:
    with open(CLIENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(clients, f, ensure_ascii=False, indent=2)

def load_metrics() -> pd.DataFrame:
    if not os.path.exists(METRICS_FILE):
        return pd.DataFrame()
    with open(METRICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data:
        return pd.DataFrame()
    df = pd.DataFrame(data)
    df["views"]    = pd.to_numeric(df["views"],    errors="coerce").fillna(0).astype(int)
    df["likes"]    = pd.to_numeric(df["likes"],    errors="coerce").fillna(0).astype(int)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)
    return df

def save_metric(record: dict) -> None:
    data = []
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    data.append(record)
    with open(METRICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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

    if st.button("📊  לוח בקרה",       key="nav_dash"):    st.session_state.page = "dashboard"
    if st.button("✍️  הזנת נתונים",    key="nav_entry"):   st.session_state.page = "entry"
    if st.button("👥  ניהול לקוחות",   key="nav_clients"): st.session_state.page = "clients"

    st.markdown("---")
    clients_list = load_clients()
    metrics_df   = load_metrics()
    st.markdown(f"<p style='color:{TEXT_DIM};font-size:0.75rem;text-align:right;'>לקוחות: <strong style='color:{TEXT_LIGHT};'>{len(clients_list)}</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_DIM};font-size:0.75rem;text-align:right;'>רשומות: <strong style='color:{TEXT_LIGHT};'>{len(metrics_df)}</strong></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{TEXT_DIM};font-size:0.75rem;text-align:right;'>עדכון: {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    col_title, col_badge = st.columns([3, 1])
    with col_title:
        st.markdown(f"# {title}")
        st.markdown(f"<p style='color:{TEXT_DIM};margin-top:-12px;'>{subtitle}</p>", unsafe_allow_html=True)
    with col_badge:
        st.markdown(f"""
        <div class='brand-badge' style='padding-top:20px;text-align:left;'>
            <span class='en'>Tape Up Media</span>
            <span class='he'> — טייפ אפ מדיה</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.page == "dashboard":
    page_header("📊 לוח בקרה — ביצועי וידאו", "סקירת נתוני צפיות לכל הלקוחות")
    df = load_metrics()

    if df.empty:
        st.info("אין נתונים להצגה. אנא הזן נתונים בלשונית הזנת נתונים.")
    else:
        client_names   = sorted(df["client"].unique().tolist())
        platform_names = sorted(df["platform"].unique().tolist())

        fc1, fc2 = st.columns(2)
        with fc1:
            selected_clients   = st.multiselect("לקוחות", client_names, default=client_names)
        with fc2:
            selected_platforms = st.multiselect("פלטפורמות", platform_names, default=platform_names)

        filtered = df[df["client"].isin(selected_clients) & df["platform"].isin(selected_platforms)]

        if filtered.empty:
            st.info("אין נתונים לסינון הנוכחי.")
        else:
            st.markdown("&nbsp;")

            # ── KPIs ──────────────────────────────────────────────────────────────────
            total_views    = filtered["views"].sum()
            total_likes    = filtered["likes"].sum()
            total_comments = filtered["comments"].sum()
            engagement     = ((total_likes + total_comments) / total_views * 100) if total_views else 0

            k1, k2, k3, k4 = st.columns(4)
            views_fmt = f"{total_views/1_000_000:.2f}M" if total_views >= 1_000_000 else f"{total_views/1_000:.1f}K"
            likes_fmt = f"{total_likes/1_000:.1f}K"     if total_likes >= 1_000     else str(total_likes)
            cmts_fmt  = f"{total_comments/1_000:.1f}K"  if total_comments >= 1_000  else str(total_comments)
            k1.metric("סה״כ צפיות",    views_fmt)
            k2.metric("סה״כ לייקים",   likes_fmt)
            k3.metric("סה״כ תגובות",   cmts_fmt)
            k4.metric("ממוצע מעורבות", f"{engagement:.2f}%")

            st.markdown("&nbsp;")

            # ── AI Insights ───────────────────────────────────────────────────────────
            st.markdown("### 🧠 תובנות המערכת")
            tt_views    = filtered[filtered["platform"] == "tiktok"]["views"].sum()
            ig_views    = filtered[filtered["platform"] == "instagram"]["views"].sum()
            top_client  = filtered.groupby("client")["views"].sum().idxmax()
            top_views_k = filtered[filtered["client"] == top_client]["views"].sum() / 1000
            better   = "טיקטוק" if tt_views >= ig_views else "אינסטגרם"
            worse    = "אינסטגרם" if tt_views >= ig_views else "טיקטוק"
            pct_diff = abs(tt_views - ig_views) / max(ig_views, tt_views, 1) * 100

            st.markdown(f"""
            <div class='insight-box'>
                <div class='insight-title'>⚡ תובנות אוטומטיות</div>
                <div class='insight-body'>
                    📈 <strong>{better}</strong> מציג ביצועים טובים יותר מ{worse} ב־<strong>{pct_diff:.0f}%</strong> — מומלץ להגביר את קצב ההעלאות לפלטפורמה זו.<br>
                    🏆 הלקוח המוביל הוא <strong>{top_client}</strong> עם <strong>{top_views_k:,.0f}K</strong> צפיות — כדאי לנתח את התוכן שעובד עבורו וליישם אצל לקוחות נוספים.<br>
                    💡 שיעור המעורבות עומד על <strong>{engagement:.2f}%</strong> — סרטונים קצרים מתחת ל-30 שניות מציגים מעורבות גבוהה ב-40% בממוצע.
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Charts ────────────────────────────────────────────────────────────────
            c1, c2 = st.columns([2, 1])

            with c1:
                st.markdown("### צפיות לאורך זמן")
                time_df = filtered.groupby(["date", "platform"])["views"].sum().reset_index().sort_values("date")
                fig_line = px.line(time_df, x="date", y="views", color="platform",
                                   color_discrete_map=PLATFORM_COLORS, markers=True,
                                   labels={"date": "תאריך", "views": "צפיות", "platform": "פלטפורמה"})
                fig_line.update_layout(**PLOTLY_THEME, margin=dict(l=60,r=20,t=20,b=60), height=320,
                                       xaxis=dict(tickfont=dict(color=TEXT_MID), gridcolor="#1f1f1f"),
                                       yaxis=dict(tickfont=dict(color=TEXT_LIGHT, size=11), gridcolor="#1f1f1f", tickformat=".2s"))
                fig_line.update_traces(line_width=2.5)
                st.plotly_chart(fig_line, use_container_width=True, config=CHART_CONFIG)

            with c2:
                st.markdown("### פיצול פלטפורמות")
                plat_df = filtered.groupby("platform")["views"].sum().reset_index()
                fig_pie = px.pie(plat_df, names="platform", values="views",
                                 color="platform", color_discrete_map=PLATFORM_COLORS, hole=0.62,
                                 labels={"platform": "פלטפורמה", "views": "צפיות"})
                fig_pie.update_layout(**PLOTLY_THEME, margin=dict(l=0,r=0,t=20,b=60), height=320)
                fig_pie.update_traces(textinfo="percent", textfont_color="#fff")
                st.plotly_chart(fig_pie, use_container_width=True, config=CHART_CONFIG)

            st.markdown("### צפיות לפי לקוח")
            client_df = filtered.groupby(["client", "platform"])["views"].sum().reset_index().sort_values("views", ascending=True)
            fig_bar = px.bar(client_df, x="views", y="client", color="platform",
                             orientation="h", barmode="group", color_discrete_map=PLATFORM_COLORS,
                             labels={"views": "צפיות", "client": "לקוח", "platform": "פלטפורמה"},
                             text_auto=".2s")
            fig_bar.update_traces(textposition="outside", textfont=dict(color=TEXT_LIGHT, size=11))
            fig_bar.update_layout(**PLOTLY_THEME, margin=dict(l=120,r=40,t=20,b=60), height=320,
                                  xaxis=dict(tickfont=dict(color=TEXT_MID), gridcolor="#1f1f1f"),
                                  yaxis=dict(tickfont=dict(color=TEXT_LIGHT, size=12), automargin=True),
                                  uniformtext_minsize=9, uniformtext_mode="hide")
            st.plotly_chart(fig_bar, use_container_width=True, config=CHART_CONFIG)

            st.markdown("### סרטונים מובילים")
            top = (filtered[["client","platform","date","video_id","views","likes","comments"]]
                   .sort_values("views", ascending=False).head(10).reset_index(drop=True))
            st.dataframe(top, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DATA ENTRY
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "entry":
    page_header("✍️ הזנת נתונים", "הוספת נתוני ביצועים לסרטון")

    clients_list = load_clients()
    client_names = [c["name"] for c in clients_list]

    if not client_names:
        st.warning("לא נמצאו לקוחות. אנא הוסף לקוחות בלשונית ניהול לקוחות תחילה.")
        st.stop()

    with st.form("data_entry_form", clear_on_submit=True):
        st.markdown(f"<div class='card'>", unsafe_allow_html=True)

        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            client   = st.selectbox("לקוח", client_names)
        with r1c2:
            platform = st.selectbox("פלטפורמה", ["instagram", "tiktok"])
        with r1c3:
            date     = st.date_input("תאריך", value=datetime.today())

        r2c1, r2c2 = st.columns([1, 1])
        with r2c1:
            video_id = st.text_input("שם / מזהה סרטון", placeholder="לדוג׳: reel_june21 או TT-12345")
        with r2c2:
            views    = st.number_input("צפיות", min_value=0, step=1)

        r3c1, r3c2 = st.columns(2)
        with r3c1:
            likes    = st.number_input("לייקים", min_value=0, step=1)
        with r3c2:
            comments = st.number_input("תגובות", min_value=0, step=1)

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("&nbsp;")
        submitted = st.form_submit_button("💾  שמור נתונים")

        if submitted:
            if not video_id.strip():
                st.error("יש להזין שם או מזהה לסרטון.")
            else:
                save_metric({
                    "client":   client,
                    "platform": platform,
                    "date":     str(date),
                    "video_id": video_id.strip(),
                    "views":    int(views),
                    "likes":    int(likes),
                    "comments": int(comments),
                })
                st.success(f"✅ הנתונים נשמרו בהצלחה עבור '{client}' — {video_id.strip()}")

    # ── Recent entries preview ─────────────────────────────────────────────────
    st.markdown("### רשומות אחרונות")
    recent = load_metrics()
    if recent.empty:
        st.markdown(f"<p style='color:{TEXT_DIM};'>עדיין לא הוזנו נתונים.</p>", unsafe_allow_html=True)
    else:
        st.dataframe(
            recent.sort_values("date", ascending=False).head(15).reset_index(drop=True),
            use_container_width=True,
            hide_index=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: CLIENT MANAGEMENT
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.page == "clients":
    page_header("👥 ניהול לקוחות", "הוספה, צפייה ומחיקה של לקוחות")

    with st.form("add_client_form", clear_on_submit=True):
        st.markdown("### ➕ הוספת לקוח חדש")
        f1, f2, f3 = st.columns(3)
        with f1: new_name = st.text_input("שם לקוח", placeholder="לדוג׳: Brand Alpha")
        with f2: new_ig   = st.text_input("חשבון אינסטגרם", placeholder="@username")
        with f3: new_tt   = st.text_input("חשבון טיקטוק", placeholder="@username")

        if st.form_submit_button("✚  הוסף לקוח"):
            if not new_name.strip():
                st.error("שם הלקוח הוא שדה חובה.")
            else:
                clients = load_clients()
                if new_name.strip().lower() in [c["name"].lower() for c in clients]:
                    st.error(f"לקוח בשם '{new_name}' כבר קיים.")
                else:
                    clients.append({"name": new_name.strip(), "instagram": new_ig.strip(), "tiktok": new_tt.strip()})
                    save_clients(clients)
                    st.success(f"✅ הלקוח '{new_name}' נוסף בהצלחה!")
                    st.rerun()

    st.markdown("&nbsp;")
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
                    <div style='color:#fff;font-weight:700;font-size:1rem;'>{client['name']}</div>
                    <div style='margin-top:6px;'>{ig_tag}{tt_tag}</div>
                </div>""", unsafe_allow_html=True)
            with col_btn:
                st.markdown("<div class='delete-btn'>", unsafe_allow_html=True)
                if st.button("🗑 מחק", key=f"del_{i}"):
                    clients.pop(i)
                    save_clients(clients)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
