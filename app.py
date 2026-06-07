"""
YouTube Trending — Global Analytics Dashboard (Streamlit gallery)

Presents the exported Power BI dashboard pages as an interactive, shareable gallery.
Run locally:   streamlit run app.py
Deploy free:   push to GitHub -> https://share.streamlit.io -> point at app.py
"""

from pathlib import Path
import streamlit as st

# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
APP_DIR = Path(__file__).parent
SHOTS = APP_DIR / "screenshots"

st.set_page_config(
    page_title="YouTube Trending — Global Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Each page: file name (in /screenshots), one-line summary, and bullet takeaways.
PAGES = {
    "📊 Overview": {
        "file": "Overview.png",
        "summary": "Executive summary across all 10 countries — KPIs, world map, "
                   "views-over-time with a 7-day moving average, and top categories.",
        "bullets": [
            "Headline KPIs: total views, engagement rate, unique videos & channels, countries covered.",
            "World map of total views by country.",
            "Daily views trend with a 7-day moving average overlay.",
            "Top categories by total views, with global country/category slicers.",
        ],
    },
    "🌍 Country Comparison": {
        "file": "Country Comparison.png",
        "summary": "How the 10 countries differ — reach vs engagement, a country × category "
                   "heat matrix, an efficiency-quadrant scatter, and per-country trend lines.",
        "bullets": [
            "Views vs engagement rate by country (dual-axis combo).",
            "Country × category matrix, conditionally colour-formatted.",
            "Avg-views-per-video vs engagement scatter (efficiency quadrants).",
            "Small-multiple daily trend lines, one panel per country.",
        ],
    },
    "🏷️ Category & Content": {
        "file": "Category & Content.png",
        "summary": "What content performs — engagement and like/dislike by category, a treemap "
                   "of total views, and the view-size distribution of trending videos.",
        "bullets": [
            "Engagement Rate % by category (reach ≠ engagement).",
            "Like / Dislike Ratio by category (audience sentiment).",
            "Treemap of total views by category.",
            "Histogram of trending entries by view-size bucket.",
        ],
    },
    "📺 Channels & Top Videos": {
        "file": "Channels & Top Videos.png",
        "summary": "Who wins — top channels by views/engagement (with rank & data bars) and a "
                   "top-videos table with rendered thumbnails. Drill-through target.",
        "bullets": [
            "Top channels: total views, unique videos, engagement, rank.",
            "Top videos table with live thumbnails.",
            "One row per video (de-duplicated across trending days).",
            "Drill-through destination from the other pages.",
        ],
    },
    "⏱️ Timing & Virality": {
        "file": "Timing & Virality.png",
        "summary": "When & how fast — a publish weekday × hour heatmap, a days-to-trend "
                   "distribution, average days-to-trend over time, and speed vs engagement.",
        "bullets": [
            "Publish weekday × hour heatmap (best time to publish).",
            "Days-to-trend histogram (median ~1 day).",
            "Average days-to-trend over time.",
            "Speed-to-trend vs engagement scatter.",
        ],
    },
}

KPIS = [
    ("Countries", "10"),
    ("Cleaned rows", "342,656"),
    ("Unique videos", "171K"),
    ("Unique channels", "34K"),
    ("Avg engagement", "3.18%"),
]

INSIGHTS = [
    "🎵 **Music & Entertainment** dominate global trending views.",
    "🌍 **Country mix differs sharply** — India/Russia skew to Entertainment & Film; US/GB to Music & Comedy.",
    "🤝 **Nonprofits & Education** drive the highest *engagement rate*, despite lower raw views.",
    "⚡ Most videos trend **fast** — median ~1 day, average ~7.6 days to trend.",
    "🏷️ Most trending videos sit in the **100K–1M views** band; 20M+ is rare.",
]

# --------------------------------------------------------------------------- #
# Sidebar
# --------------------------------------------------------------------------- #
st.sidebar.title("🎬 YouTube Trending")
st.sidebar.caption("Global Analytics Dashboard · 10 countries")
view = st.sidebar.radio(
    "Go to",
    ["🏠 Project Home", *PAGES.keys()],
    label_visibility="collapsed",
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Stack:** Python · pandas · ftfy · Power BI · Streamlit  \n"
    "**Data:** [YouTube Trending — Kaggle](https://www.kaggle.com/datasets/datasnaek/youtube-new)  \n"
    "**Window:** 2017-11 → 2018-06"
)


def show_image(file_name: str):
    """Render a screenshot, with a clear message if it's missing."""
    path = SHOTS / file_name
    if path.exists():
        st.image(str(path), use_container_width=True)
    else:
        st.warning(f"Screenshot not found: `screenshots/{file_name}`")


# --------------------------------------------------------------------------- #
# Home
# --------------------------------------------------------------------------- #
if view == "🏠 Project Home":
    st.title("🎬 YouTube Trending — Global Analytics Dashboard")
    st.markdown(
        "An end-to-end analytics project on the **YouTube Trending Videos** dataset across "
        "**all 10 countries** (US, GB, CA, DE, FR, IN, JP, KR, MX, RU): "
        "Python cleaning → Power BI modelling → a 5-page interactive dashboard."
    )

    cols = st.columns(len(KPIS))
    for col, (label, value) in zip(cols, KPIS):
        col.metric(label, value)

    st.markdown("### 💡 Key Insights")
    for line in INSIGHTS:
        st.markdown(f"- {line}")

    st.markdown("### 📊 Dashboard Pages")
    st.caption("Use the sidebar to open each page full-screen. Previews below:")

    grid = st.columns(2)
    for i, (name, meta) in enumerate(PAGES.items()):
        with grid[i % 2]:
            st.markdown(f"**{name}**")
            show_image(meta["file"])
            st.caption(meta["summary"])

    st.markdown("---")
    st.markdown(
        "🔧 **Cleaning pipeline:** joins 10 countries, repairs `latin1` mojibake with `ftfy`, "
        "maps per-country categories, derives engagement metrics & `days_to_trend`, drops nulls / "
        "duplicates / impossible rows → **375,942 → 342,656 rows, 0 nulls**. "
        "See `cleaning_script/cleaning_all_countries.py` and `BUILD_GUIDE.md`."
    )

# --------------------------------------------------------------------------- #
# Individual page
# --------------------------------------------------------------------------- #
else:
    meta = PAGES[view]
    st.title(view.split(" ", 1)[1])  # drop the emoji for the H1
    st.markdown(f"*{meta['summary']}*")
    show_image(meta["file"])
    st.markdown("#### Highlights")
    for b in meta["bullets"]:
        st.markdown(f"- {b}")
