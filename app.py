import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
from collections import Counter

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

st.set_page_config(
    page_title="Elias Intelligence",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .stApp {
    background-color: #0D0D0D !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #E8E8E4 !important;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
section[data-testid="stSidebar"] { display: none; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Page wrapper for centering content ── */
.content-area {
    max-width: 960px;
    margin: 0 auto;
    padding: 32px 24px;
}

/* Force streamlit columns inside content-area to respect width */
.content-area .stColumns, 
.content-area [data-testid="column"] {
    min-width: 0;
}

/* ── Header ── */
.elias-header {
    background: #111111;
    border-bottom: 2px solid #C41E3A;
    padding: 16px 160px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.elias-wordmark {
    font-family: 'Playfair Display', serif;
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.elias-wordmark span { color: #C41E3A; }

.elias-tagline {
    font-size: 10px;
    font-weight: 500;
    color: #555;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}

/* ── Metric bar ── */
.metric-bar {
    background: #111111;
    border-bottom: 1px solid #222;
    padding: 16px 160px;
    display: flex;
    gap: 48px;
    align-items: center;
}

.metric-item { display: flex; flex-direction: column; gap: 2px; }

.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 600;
    color: #FFFFFF;
    line-height: 1;
}

.metric-label {
    font-size: 9px;
    font-weight: 600;
    color: #555;
    letter-spacing: 0.18em;
    text-transform: uppercase;
}

.metric-divider {
    width: 1px;
    height: 36px;
    background: #222;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #111111 !important;
    border-bottom: 1px solid #222 !important;
    gap: 0 !important;
    padding: 0 160px !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: #444 !important;
    padding: 16px 20px !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}

.stTabs [aria-selected="true"] {
    color: #C41E3A !important;
    border-bottom: 2px solid #C41E3A !important;
}

.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Week selector ── */
.week-label {
    font-size: 9px;
    font-weight: 700;
    color: #555;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 8px;
}

/* Override selectbox */
.stSelectbox > div > div {
    background: #1A1A1A !important;
    border: 1px solid #333 !important;
    border-radius: 2px !important;
    color: #E8E8E4 !important;
}
.stSelectbox > div > div:hover { border-color: #555 !important; }
.stSelectbox label {
    color: #555 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
}

/* Override multiselect */
.stMultiSelect > div > div {
    background: #1A1A1A !important;
    border: 1px solid #333 !important;
    border-radius: 2px !important;
    color: #E8E8E4 !important;
}
.stMultiSelect span[data-baseweb="tag"] {
    background-color: #2A2A2A !important;
    color: #AAAAAA !important;
    border: 1px solid #444 !important;
}
.stMultiSelect span[data-baseweb="tag"] span { color: #AAAAAA !important; }
.stMultiSelect label {
    color: #555 !important;
    font-size: 9px !important;
    font-weight: 700 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
}

.stCheckbox label { color: #888 !important; font-size: 11px !important; }

/* ── Executive summary ── */
.exec-summary {
    background: #141414;
    border: 1px solid #222;
    border-left: 3px solid #C41E3A;
    padding: 28px 32px;
    margin-bottom: 32px;
}
.exec-summary-label {
    font-size: 9px;
    font-weight: 700;
    color: #C41E3A;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 14px;
}
.exec-summary-text { font-size: 14px; color: #CCCCCC; line-height: 1.8; }
.exec-summary-text p { margin-bottom: 12px; }
.exec-summary-text p:last-child { margin-bottom: 0; }

/* ── Section header ── */
.section-header {
    display: flex;
    align-items: baseline;
    gap: 14px;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 1px solid #1E1E1E;
}
.section-title {
    font-family: 'Playfair Display', serif;
    font-size: 18px;
    font-weight: 600;
    color: #FFFFFF;
}
.section-sub { font-size: 11px; color: #444; letter-spacing: 0.08em; text-transform: uppercase; }

/* ── Insight card ── */
.insight-card {
    background: #141414 !important;
    border: 1px solid #1E1E1E !important;
    border-left: 3px solid #333 !important;
    padding: 18px 22px !important;
    margin-bottom: 10px !important;
    position: relative !important;
}
.insight-card.featured { border-left-color: #C41E3A !important; }

.insight-number {
    font-family: 'Playfair Display', serif !important;
    font-size: 11px !important;
    color: #C41E3A !important;
    letter-spacing: 0.1em !important;
    margin-bottom: 8px !important;
}
.insight-top {
    display: flex !important;
    justify-content: space-between !important;
    align-items: flex-start !important;
    gap: 16px !important;
    margin-bottom: 10px !important;
}
.insight-recommendation {
    font-size: 15px !important;
    font-weight: 600 !important;
    color: #FFFFFF !important;
    line-height: 1.6 !important;
    flex: 1 !important;
}
.insight-link {
    font-size: 10px !important;
    color: #C41E3A !important;
    text-decoration: none !important;
    white-space: nowrap !important;
    padding-top: 4px !important;
    letter-spacing: 0.08em !important;
    opacity: 0.8 !important;
}
.insight-link:hover { opacity: 1 !important; }

.support-quotes {
    margin: 10px 0 14px 0 !important;
    padding-left: 16px !important;
    border-left: 2px solid #2A2A2A !important;
}
.support-quote {
    font-size: 12px !important;
    color: #777 !important;
    font-style: italic !important;
    line-height: 1.6 !important;
    margin-bottom: 6px !important;
    padding: 2px 0 !important;
}
.support-quote:last-child { margin-bottom: 0 !important; }

.insight-meta {
    display: flex !important;
    gap: 8px !important;
    align-items: center !important;
    flex-wrap: wrap !important;
    margin-top: 12px !important;
    padding-top: 12px !important;
    border-top: 1px solid #1E1E1E !important;
}

.tag {
    font-size: 9px !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 3px 8px !important;
    border-radius: 2px !important;
}
.tag-experience { background: #1E1E1E !important; color: #888 !important; border: 1px solid #333 !important; }
.tag-category   { background: #1A1A1A !important; color: #666 !important; border: 1px solid #2A2A2A !important; }
.tag-project    { background: #1A0A0A !important; color: #C41E3A !important; border: 1px solid #3A1A1A !important; }
.tag-featured   { background: #C41E3A !important; color: #FFF !important; border: none !important; }

.insight-byline { margin-left: auto !important; font-size: 10px !important; color: #444 !important; white-space: nowrap !important; }
.insight-byline .upvote-count { color: #C41E3A !important; font-weight: 600 !important; }

/* ── Chart card ── */
.chart-card {
    background: #141414 !important;
    border: 1px solid #1E1E1E !important;
    padding: 20px 24px !important;
    margin-bottom: 12px !important;
}
.chart-title {
    font-size: 9px !important;
    font-weight: 700 !important;
    color: #444 !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    margin-bottom: 16px !important;
    padding-bottom: 10px !important;
    border-bottom: 1px solid #1E1E1E !important;
}

/* ── Drift alert ── */
.drift-alert {
    background: #1A0A0A;
    border: 1px solid #3A1A1A;
    border-left: 3px solid #C41E3A;
    padding: 12px 16px;
    margin-bottom: 8px;
}
.drift-alert-title { font-size: 12px; font-weight: 600; color: #C41E3A; margin-bottom: 3px; }
.drift-alert-body { font-size: 11px; color: #666; }

.context-paragraph {
    font-size: 13px;
    color: #999;
    line-height: 1.8;
    margin: 10px 0 14px 0;
    padding: 12px 16px;
    background: #0D0D0D;
    border-left: 2px solid #C41E3A;
}
.standard-details { margin: 8px 0 12px 0; }
.standard-bullet { font-size: 12px; color: #777; line-height: 1.6; margin-bottom: 5px; padding-left: 4px; }
.standard-quote { font-style: italic; color: #555; padding-left: 8px; border-left: 2px solid #222; }

.empty-state {
    padding: 80px;
    text-align: center;
    color: #333;
    font-size: 12px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.stDataFrame { background: #141414 !important; }
div[data-testid="stMarkdownContainer"] p { color: #CCCCCC; }
.stPlotlyChart { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="elias-header">
    <div class="elias-wordmark">ELI<span>A</span>S</div>
    <div class="elias-tagline">Guest Intelligence Platform &nbsp;·&nbsp; Disney Parks</div>
</div>
""", unsafe_allow_html=True)


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data(ttl=180)
def load_insights():
    result = supabase.table("insights")\
        .select("*")\
        .order("weighted_score", desc=True)\
        .execute()
    if result.data:
        df = pd.DataFrame(result.data)
        for col in ['date_posted', 'date_added']:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
        return df
    return pd.DataFrame()

@st.cache_data(ttl=180)
def load_raw_count():
    result = supabase.table("raw_comments").select("id", count="exact").execute()
    return result.count or 0

df = load_insights()
raw_count = load_raw_count()


# ── Metric bar ────────────────────────────────────────────────────────────────
if not df.empty:
    total       = len(df)
    featured    = len(df[df['featured'] == True]) if 'featured' in df.columns else 0
    signal_rate = round((total / raw_count * 100), 1) if raw_count > 0 else 0

    st.markdown(f"""
    <div class="metric-bar">
        <div class="metric-item">
            <div class="metric-value">{total}</div>
            <div class="metric-label">Total Insights</div>
        </div>
        <div class="metric-divider"></div>
        <div class="metric-item">
            <div class="metric-value">{featured}</div>
            <div class="metric-label">Featured</div>
        </div>
        <div class="metric-divider"></div>
        <div class="metric-item">
            <div class="metric-value">{raw_count:,}</div>
            <div class="metric-label">Comments Scanned</div>
        </div>
        <div class="metric-divider"></div>
        <div class="metric-item">
            <div class="metric-value">{signal_rate}%</div>
            <div class="metric-label">Signal Rate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="metric-bar">
        <div class="metric-item">
            <div class="metric-value">—</div>
            <div class="metric-label">No data yet — run the scorer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Week definitions — built from actual Supabase data ───────────────────────
def get_week_options(df):
    """Build week options from actual date range in the data."""
    weeks = []
    if df.empty:
        return weeks

    date_col = None
    for c in ['date_posted', 'date_added']:
        if c in df.columns and df[c].notna().any():
            date_col = c
            break
    if not date_col:
        return weeks

    dates = df[date_col].dropna()
    if dates.empty:
        return weeks

    # Find the Monday of the most recent week that has data
    latest = dates.max().date()
    earliest = dates.min().date()

    # Walk back from latest in 7-day chunks covering all data
    # Anchor to Sunday->Saturday weeks
    days_since_sun = latest.weekday() + 1 if latest.weekday() != 6 else 0
    week_end = latest + timedelta(days=(6 - latest.weekday() - 1) % 7)
    if week_end < latest:
        week_end += timedelta(weeks=1)

    seen = set()
    current_end = week_end
    while current_end - timedelta(days=6) >= earliest - timedelta(days=7):
        current_start = current_end - timedelta(days=6)
        label = f"{current_start.strftime('%b %d')} – {current_end.strftime('%b %d, %Y')}"
        if label not in seen:
            weeks.append((label, current_start, current_end))
            seen.add(label)
        current_end -= timedelta(weeks=1)
        if len(weeks) > 20:
            break

    return weeks


# ── Inline styles ─────────────────────────────────────────────────────────────
S = {
    'card':         'background:#141414;border:1px solid #1E1E1E;border-left:3px solid #333;padding:18px 22px;margin-bottom:10px;',
    'card_featured':'background:#141414;border:1px solid #1E1E1E;border-left:3px solid #C41E3A;padding:18px 22px;margin-bottom:10px;',
    'rank':         'font-size:11px;color:#C41E3A;letter-spacing:0.1em;margin-bottom:8px;font-family:serif;',
    'top':          'display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:10px;',
    'rec':          'font-size:15px;font-weight:600;color:#FFFFFF;line-height:1.6;flex:1;',
    'link':         'font-size:10px;color:#C41E3A;text-decoration:none;white-space:nowrap;padding-top:4px;letter-spacing:0.08em;',
    'context':      'font-size:13px;color:#999;line-height:1.8;margin:10px 0 14px 0;padding:12px 16px;background:#0D0D0D;border-left:2px solid #C41E3A;',
    'quotes':       'margin:10px 0 14px 0;padding-left:16px;border-left:2px solid #2A2A2A;',
    'quote':        'font-size:12px;color:#777;font-style:italic;line-height:1.6;margin-bottom:6px;',
    'bullet':       'font-size:12px;color:#777;line-height:1.6;margin-bottom:5px;padding-left:4px;',
    'source_q':     'font-size:12px;color:#555;font-style:italic;line-height:1.6;margin-bottom:5px;padding-left:12px;border-left:2px solid #222;',
    'meta':         'display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-top:12px;padding-top:12px;border-top:1px solid #1E1E1E;',
    'tag_base':     'font-size:9px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:3px 8px;border-radius:2px;',
    'tag_exp':      'background:#1E1E1E;color:#888;border:1px solid #333;',
    'tag_cat':      'background:#1A1A1A;color:#666;border:1px solid #2A2A2A;',
    'tag_proj':     'background:#1A0A0A;color:#C41E3A;border:1px solid #3A1A1A;',
    'tag_feat':     'background:#C41E3A;color:#FFF;',
    'byline':       'margin-left:auto;font-size:10px;color:#444;white-space:nowrap;',
    'upvote':       'color:#C41E3A;font-weight:600;',
}

# ── Render card ───────────────────────────────────────────────────────────────
def render_card(row, rank=None):
    is_high_tier = float(row.get('upvote_percentile', 0) or 0) >= 75
    card_style   = S['card_featured'] if row.get('featured') else S['card']

    rank_html = f'<div style="{S["rank"]}">#{rank}</div>' if rank else ""

    exp_tag  = f'<span style="{S["tag_base"]}{S["tag_exp"]}">{row.get("experience_tag","—")}</span>'
    cat_tag  = f'<span style="{S["tag_base"]}{S["tag_cat"]}">{str(row.get("category_tag","—")).replace("_"," ").title()}</span>'
    feat_tag = f'<span style="{S["tag_base"]}{S["tag_feat"]}">◆ Featured</span>' if row.get('featured') else ""

    proj_html = ""
    raw_proj = row.get('project_tags')
    if raw_proj:
        if isinstance(raw_proj, list):
            projects = raw_proj
        elif isinstance(raw_proj, str):
            projects = [p.strip().strip('"') for p in raw_proj.strip('{}').split(',') if p.strip()]
        else:
            projects = []
        for p in projects:
            if p:
                proj_html += f'<span style="{S["tag_base"]}{S["tag_proj"]}">{p}</span>'

    link_html = ""
    if row.get('comment_url'):
        link_html = f'<a style="{S["link"]}" href="{row["comment_url"]}" target="_blank">View source →</a>'

    byline_parts = []
    if row.get('username'):
        byline_parts.append(f'u/{row["username"]}')
    date_val = row.get('date_posted')
    if date_val is None or (isinstance(date_val, float) and pd.isna(date_val)):
        date_val = row.get('date_added')
    if date_val is not None:
        try:
            d = pd.to_datetime(date_val, utc=True)
            byline_parts.append(d.strftime('%b %d, %Y'))
        except:
            pass
    upvotes     = int(row.get('upvotes', 0) or 0)
    upvote_html = f'<span style="{S["upvote"]}">▲ {upvotes:,}</span>'
    byline_str  = " · ".join(byline_parts)
    byline_html = f'<span style="{S["byline"]}">{byline_str} &nbsp; {upvote_html}</span>'

    if is_high_tier:
        context_html = ""
        if row.get('context_paragraph'):
            context_html = f'<div style="{S["context"]}">{row["context_paragraph"]}</div>'

        quotes_html = ""
        raw_sq = row.get('supporting_quotes')
        if raw_sq:
            if isinstance(raw_sq, list):
                sq_list = [q for q in raw_sq if q]
            elif isinstance(raw_sq, str):
                sq_list = [q.strip().strip('"') for q in raw_sq.strip('{}').split(',') if q.strip()]
            else:
                sq_list = []
            if sq_list:
                bullets = "".join([f'<div style="{S["quote"]}">"{q}"</div>' for q in sq_list[:3]])
                quotes_html = f'<div style="{S["quotes"]}">{bullets}</div>'

        st.markdown(f"""
        <div style="{card_style}">
            {rank_html}
            <div style="{S['top']}">
                <div style="{S['rec']}">{row.get('recommendation','—')}</div>
                {link_html}
            </div>
            {context_html}
            {quotes_html}
            <div style="{S['meta']}">
                {exp_tag}{cat_tag}{feat_tag}{proj_html}
                {byline_html}
            </div>
        </div>
        """, unsafe_allow_html=True)

    else:
        detail_html = ""
        if row.get('context_bullet'):
            detail_html += f'<div style="{S["bullet"]}">→ {row["context_bullet"]}</div>'
        if row.get('source_quote'):
            detail_html += f'<div style="{S["source_q"]}">"{row["source_quote"]}"</div>'

        st.markdown(f"""
        <div style="{card_style}">
            {rank_html}
            <div style="{S['top']}">
                <div style="{S['rec']}">{row.get('recommendation','—')}</div>
                {link_html}
            </div>
            {detail_html}
            <div style="{S['meta']}">
                {exp_tag}{cat_tag}{feat_tag}{proj_html}
                {byline_html}
            </div>
        </div>
        """, unsafe_allow_html=True)


# ── Executive summary ─────────────────────────────────────────────────────────
def build_exec_summary(week_df, week_label):
    if week_df.empty:
        return None

    total      = len(week_df)
    top_cats   = week_df['category_tag'].value_counts().head(3).index.tolist() if 'category_tag' in week_df.columns else []
    top_proj   = None
    proj_count = {}
    if 'project_tags' in week_df.columns:
        all_tags = []
        for val in week_df['project_tags'].dropna():
            if isinstance(val, list): all_tags.extend(val)
            elif isinstance(val, str):
                all_tags.extend([p.strip().strip('"') for p in val.strip('{}').split(',') if p.strip()])
        if all_tags:
            proj_count = Counter(all_tags)
            top_proj = proj_count.most_common(1)[0][0]

    # Top 3 recommendations by upvotes
    top3 = week_df.sort_values('upvotes', ascending=False).head(3)
    top3_recs = []
    for _, r in top3.iterrows():
        rec  = r.get('recommendation', '')
        upv  = int(r.get('upvotes', 0) or 0)
        cat  = str(r.get('category_tag', '')).replace('_', ' ').title()
        proj = ''
        raw_p = r.get('project_tags')
        if raw_p:
            if isinstance(raw_p, list) and raw_p: proj = raw_p[0]
            elif isinstance(raw_p, str): proj = raw_p.strip('{}').split(',')[0].strip().strip('"')
        top3_recs.append((rec, upv, cat, proj))

    # Top areas by mention count
    top_areas = [p for p, _ in proj_count.most_common(4)] if proj_count else []
    areas_str = ", ".join(top_areas[:4]) if top_areas else "General Disney"
    cat_str   = ", ".join([c.replace('_', ' ').title() for c in top_cats])

    # Build top 3 rec bullets
    rec_bullets = ""
    for rec, upv, cat, proj in top3_recs:
        short_rec = rec[:100] + ('...' if len(rec) > 100 else '')
        rec_bullets += f'<li style="margin-bottom:10px;color:#CCCCCC;"><strong style="color:#FFFFFF;">{short_rec}</strong> <span style="color:#555;font-size:11px;">— {cat}{(" · " + proj) if proj and proj != "General Disney" else ""} · ▲ {upv:,}</span></li>'

    summary = f"""
<p style="margin-bottom:16px;">
<strong style="color:#E8E8E4;">{total} insight{"s" if total != 1 else ""}</strong> surfaced for 
<strong style="color:#E8E8E4;">{week_label}</strong>. 
The dominant signal categories were <strong style="color:#E8E8E4;">{cat_str}</strong>. 
The most-discussed areas were <strong style="color:#E8E8E4;">{areas_str}</strong>.
</p>

<p style="font-size:10px;font-weight:700;color:#C41E3A;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:10px;">Top 3 by Community Validation</p>
<ol style="padding-left:18px;margin-bottom:0;">
{rec_bullets}
</ol>
"""
    return summary


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["WEEKLY BRIEF", "GRAPHS", "SEARCH"])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — WEEKLY BRIEF
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    _l, _mid, _r = st.columns([1, 6, 1])
    with _mid:
        if df.empty:
            st.markdown('<div class="empty-state">No insights yet — run the scorer first</div>', unsafe_allow_html=True)
        else:
            WEEK_OPTIONS = get_week_options(df)
            WEEK_LABELS  = [w[0] for w in WEEK_OPTIONS]

            if WEEK_LABELS:
                st.markdown('<div class="week-label">Select Week</div>', unsafe_allow_html=True)
                selected_week_label = st.selectbox(
                    "Select Week",
                    WEEK_LABELS,
                    index=0,
                    key="week_select",
                    label_visibility="collapsed"
                )

                selected_week = next((w for w in WEEK_OPTIONS if w[0] == selected_week_label), WEEK_OPTIONS[0])
                week_start = pd.Timestamp(selected_week[1], tz='UTC')
                week_end   = pd.Timestamp(selected_week[2], tz='UTC') + pd.Timedelta(hours=23, minutes=59)

                date_col = 'date_posted' if ('date_posted' in df.columns and df['date_posted'].notna().any()) else None
                if date_col:
                    week_df = df[(df[date_col] >= week_start) & (df[date_col] <= week_end)].copy()
                else:
                    week_df = df.copy()

                if week_df.empty:
                    week_df = df.copy()
                    st.markdown('<div style="font-size:11px;color:#444;margin-bottom:16px;margin-top:-8px">No data for this week — showing all insights</div>', unsafe_allow_html=True)

                week_df = week_df.sort_values('weighted_score', ascending=False)

                summary_html = build_exec_summary(week_df, selected_week_label)
                if summary_html:
                    st.markdown(f"""
                    <div class="exec-summary">
                        <div class="exec-summary-label">Executive Summary</div>
                        <div class="exec-summary-text">{summary_html}</div>
                    </div>
                    """, unsafe_allow_html=True)

                top5 = week_df.drop_duplicates(subset=['id']).head(5) if 'id' in week_df.columns else week_df.head(5)

                st.markdown(f"""
                <div class="section-header">
                    <div class="section-title">Top Recommendations</div>
                    <div class="section-sub">{len(top5)} highest-signal findings · {selected_week_label}</div>
                </div>
                """, unsafe_allow_html=True)

                for rank, (_, row) in enumerate(top5.iterrows(), start=1):
                    render_card(row, rank=rank)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — GRAPHS
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    _l, _mid, _r = st.columns([1, 6, 1])
    with _mid:
        if df.empty:
            st.markdown('<div class="empty-state">No data yet</div>', unsafe_allow_html=True)
        else:
            # ── Row 1: Category + Experience bars ────────────────────────────────
            r1c1, r1c2 = st.columns(2)

            with r1c1:
                st.markdown('<div class="chart-card"><div class="chart-title">Insights by Category</div>', unsafe_allow_html=True)
                cat_counts = df['category_tag'].value_counts().reset_index()
                cat_counts.columns = ['category', 'count']
                cat_counts['category'] = cat_counts['category'].str.replace('_', ' ').str.title()
                fig_cat = px.bar(cat_counts, x='count', y='category', orientation='h',
                             color_discrete_sequence=['#C41E3A'])
                fig_cat.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=260,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, title='', color='#555'),
                    font=dict(family='DM Sans', size=11, color='#555'), showlegend=False)
                fig_cat.update_traces(marker_line_width=0)
                st.plotly_chart(fig_cat, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)

            with r1c2:
                st.markdown('<div class="chart-card"><div class="chart-title">Insights by Experience</div>', unsafe_allow_html=True)
                exp_counts = df['experience_tag'].value_counts().reset_index()
                exp_counts.columns = ['experience', 'count']
                fig_exp = px.bar(exp_counts, x='count', y='experience', orientation='h',
                              color_discrete_sequence=['#444444'])
                fig_exp.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=260,
                    paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, title='', color='#555'),
                    font=dict(family='DM Sans', size=11, color='#555'), showlegend=False)
                fig_exp.update_traces(marker_line_width=0)
                st.plotly_chart(fig_exp, use_container_width=True, config={'displayModeBar': False})
                st.markdown('</div>', unsafe_allow_html=True)

            # ── Row 2: Top upvoted insights bar ──────────────────────────────────
            st.markdown('<div class="chart-card"><div class="chart-title">Top 10 Most Community-Validated Insights</div>', unsafe_allow_html=True)
            top_upv = df.nlargest(10, 'upvotes')[['recommendation','upvotes','category_tag']].copy()
            top_upv['short'] = top_upv['recommendation'].str[:60] + '...'
            top_upv['category_tag'] = top_upv['category_tag'].str.replace('_',' ').str.title()
            fig_top = px.bar(top_upv, x='upvotes', y='short', orientation='h',
                             color='category_tag',
                             color_discrete_sequence=['#C41E3A','#8B1520','#5A0A14','#3A0A0A','#444','#666'])
            fig_top.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=320,
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
                yaxis=dict(showgrid=False, title='', color='#666', autorange='reversed'),
                font=dict(family='DM Sans', size=10, color='#666'),
                legend=dict(font=dict(size=9, color='#555'), title=''),
                showlegend=True)
            fig_top.update_traces(marker_line_width=0)
            st.plotly_chart(fig_top, use_container_width=True, config={'displayModeBar': False})
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Row 3: Subreddit source breakdown ────────────────────────────────
            st.markdown('<div class="chart-card"><div class="chart-title">Source Subreddit Breakdown</div>', unsafe_allow_html=True)
            try:
                raw_result = supabase.table("raw_comments").select("subreddit").execute()
                if raw_result.data:
                    raw_df = pd.DataFrame(raw_result.data)
                    sub_counts = raw_df['subreddit'].value_counts().reset_index()
                    sub_counts.columns = ['subreddit', 'count']
                    sub_counts['subreddit'] = 'r/' + sub_counts['subreddit'].astype(str)
                    fig_sub = px.bar(sub_counts, x='count', y='subreddit', orientation='h',
                                     color_discrete_sequence=['#333333'])
                    fig_sub.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=max(160, len(sub_counts)*36),
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, title='', color='#555'),
                        font=dict(family='DM Sans', size=11, color='#555'), showlegend=False)
                    fig_sub.update_traces(marker_line_width=0)
                    st.plotly_chart(fig_sub, use_container_width=True, config={'displayModeBar': False})
            except Exception as e:
                st.markdown(f'<div style="color:#444;font-size:12px">Could not load subreddit data: {e}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Row 4: Category drift ─────────────────────────────────────────────
            st.markdown('<div class="chart-card"><div class="chart-title">Category Drift — This Week vs Prior Period</div>', unsafe_allow_html=True)
            if 'date_added' in df.columns and df['date_added'].notna().any():
                now         = pd.Timestamp.now(tz='UTC')
                week_ago    = now - pd.Timedelta(days=7)
                prior_start = now - pd.Timedelta(days=14)
                this_week   = df[df['date_added'] >= week_ago]
                prior_week  = df[(df['date_added'] >= prior_start) & (df['date_added'] < week_ago)]
                if not this_week.empty and not prior_week.empty:
                    this_counts  = this_week['category_tag'].value_counts()
                    prior_counts = prior_week['category_tag'].value_counts()
                    all_cats     = set(this_counts.index) | set(prior_counts.index)
                    drift_data   = [{'category': c.replace('_',' ').title(),
                                      'This Week': this_counts.get(c,0),
                                      'Prior Week': prior_counts.get(c,0),
                                      'delta': this_counts.get(c,0) - prior_counts.get(c,0)}
                                     for c in all_cats]
                    drift_df = pd.DataFrame(drift_data).sort_values('delta', ascending=False)
                    fig_drift = go.Figure()
                    fig_drift.add_trace(go.Bar(name='This Week', x=drift_df['category'],
                                               y=drift_df['This Week'], marker_color='#C41E3A'))
                    fig_drift.add_trace(go.Bar(name='Prior Week', x=drift_df['category'],
                                               y=drift_df['Prior Week'], marker_color='#2A2A2A'))
                    fig_drift.update_layout(barmode='group', margin=dict(l=0,r=0,t=0,b=0), height=220,
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=False, color='#444'),
                        yaxis=dict(showgrid=False, zeroline=False, color='#444'),
                        font=dict(family='DM Sans', size=11, color='#555'),
                        legend=dict(font=dict(size=10, color='#555')))
                    st.plotly_chart(fig_drift, use_container_width=True, config={'displayModeBar': False})
                    for _, r in drift_df[drift_df['delta'] >= 3].iterrows():
                        st.markdown(f"""<div class="drift-alert">
                            <div class="drift-alert-title">⚠ {r['category']} spiked this week</div>
                            <div class="drift-alert-body">{int(r['This Week'])} insights vs {int(r['Prior Week'])} last period</div>
                        </div>""", unsafe_allow_html=True)
                else:
                    st.markdown('<div style="color:#333;font-size:12px;padding:12px 0">Drift detection activates after two weeks of data.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#333;font-size:12px;padding:12px 0">Date data not available.</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # ── Row 5: All insights filtered feed ────────────────────────────────
            st.markdown('<div class="section-header" style="margin-top:24px"><div class="section-title">All Insights</div></div>', unsafe_allow_html=True)
            fc1, fc2, fc3 = st.columns([2, 2, 1])
            with fc1:
                exp_filter = st.multiselect("Experience",
                    sorted(df['experience_tag'].dropna().unique().tolist()),
                    default=sorted(df['experience_tag'].dropna().unique().tolist()), key="intel_exp")
            with fc2:
                cat_filter = st.multiselect("Category",
                    sorted(df['category_tag'].dropna().unique().tolist()),
                    default=sorted(df['category_tag'].dropna().unique().tolist()), key="intel_cat")
            with fc3:
                feat_only = st.checkbox("Featured only", value=False, key="intel_feat")

            filtered = df.copy()
            if exp_filter: filtered = filtered[filtered['experience_tag'].isin(exp_filter)]
            if cat_filter: filtered = filtered[filtered['category_tag'].isin(cat_filter)]
            if feat_only:  filtered = filtered[filtered['featured'] == True]

            st.markdown(f'<div style="font-size:11px;color:#444;margin-bottom:14px">{len(filtered)} results</div>', unsafe_allow_html=True)
            for _, row in filtered.iterrows():
                render_card(row)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SEARCH
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    _l, _mid, _r = st.columns([1, 6, 1])
    with _mid:
        if df.empty:
            st.markdown('<div class="empty-state">No data yet</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="week-label">Search Insights</div>', unsafe_allow_html=True)
            search_query = st.text_input(
                "Search",
                placeholder='Try: "Polynesian Hotel", "wait time", "Genie+", "broken"...',
                key="proj_search",
                label_visibility="collapsed"
            )

            def search_insights(df, query):
                if not query or not query.strip():
                    return df.copy()
                q = query.lower().strip()
                mask = pd.Series([False] * len(df), index=df.index)
                for col in ['recommendation', 'source_quote', 'category_tag',
                            'experience_tag', 'username', 'post_title']:
                    if col in df.columns:
                        mask |= df[col].astype(str).str.lower().str.contains(q, na=False)
                if 'project_tags' in df.columns:
                    def tag_match(val):
                        if not val: return False
                        if isinstance(val, list): return any(q in str(t).lower() for t in val)
                        return q in str(val).lower()
                    mask |= df['project_tags'].apply(tag_match)
                if 'supporting_quotes' in df.columns:
                    def sq_match(val):
                        if not val: return False
                        if isinstance(val, list): return any(q in str(t).lower() for t in val)
                        return q in str(val).lower()
                    mask |= df['supporting_quotes'].apply(sq_match)
                return df[mask].copy()

            search_results = search_insights(df, search_query)

            rc1, rc2 = st.columns([3, 1])
            with rc1:
                if search_query:
                    st.markdown(f'<div style="font-size:12px;color:#C41E3A;margin:8px 0 16px">{len(search_results)} result{"s" if len(search_results) != 1 else ""} for &ldquo;{search_query}&rdquo;</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div style="font-size:11px;color:#444;margin:8px 0 16px">{len(search_results)} insights — enter a search term above to filter</div>', unsafe_allow_html=True)
            with rc2:
                sort_by = st.selectbox("Sort by", ['Upvotes', 'Most Recent', 'Quality Score'],
                                       key="proj_sort", label_visibility="collapsed")

            if sort_by == 'Upvotes':
                search_results = search_results.sort_values('upvotes', ascending=False)
            elif sort_by == 'Most Recent':
                date_col = 'date_posted' if 'date_posted' in search_results.columns else 'date_added'
                search_results = search_results.sort_values(date_col, ascending=False, na_position='last')
            else:
                search_results = search_results.sort_values('insight_quality_score', ascending=False)

            if search_results.empty:
                st.markdown('<div class="empty-state">No results found — try a different search term</div>', unsafe_allow_html=True)
            else:
                for _, row in search_results.iterrows():
                    render_card(row)
