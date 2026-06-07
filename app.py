"""
YouTube Trending — Global Analytics Dashboard (Streamlit gallery)

Presents the exported Power BI dashboard pages as an interactive, shareable gallery,
with detailed explanations of every page: visuals, slicers/filters, and tooltips.

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

# --------------------------------------------------------------------------- #
# Page content
#   file      -> screenshot in /screenshots
#   summary   -> one-line description
#   visuals   -> (visual type, what it shows) pairs
#   slicers   -> interactive filters available on the page
#   tooltips  -> what appears when you hover a data point
#   read      -> how to interpret the page / the key takeaway
# --------------------------------------------------------------------------- #
PAGES = {
    "📊 Overview": {
        "file": "Overview.png",
        "summary": "Executive summary across all 10 countries — headline KPIs, a world map, "
                   "views-over-time with a 7-day moving average, and top categories.",
        "visuals": [
            ("KPI cards", "Total Views, Engagement Rate %, Countries Covered, Unique Videos, "
                          "Unique Channels — the at-a-glance health of the whole dataset."),
            ("Dynamic subtitle card", "Shows 'All Countries' or the selected country name via "
                                      "the `Selected Country Label` DAX measure — it reacts to the slicers."),
            ("Filled/bubble map", "Total Views by country — geographic distribution of trending reach."),
            ("Line chart", "Total Views by date with a dashed `Views 7D Moving Avg` line to smooth daily noise."),
            ("Bar / scatter", "Top categories by Total Views."),
        ],
        "slicers": [
            "**Country** — multi-select list to focus on one or more of the 10 countries.",
            "**Category** — filter to specific content categories (Music, Comedy, Gaming…).",
            "**Year-Month** — narrow the trending window (Nov 2017 – Jun 2018).",
        ],
        "tooltips": "Hover any map bubble or line point to see the **country/date** and the exact "
                    "**Total Views** for that context (e.g. *India · 15-05-2018 · 97,006,036 views*).",
        "read": "Start here. Pick a country in the slicer and watch every visual — including the KPI "
                "cards and the dynamic subtitle — refilter instantly. The moving-average line tells "
                "you the trend direction without the daily spikes.",
    },
    "🌍 Country Comparison": {
        "file": "Country Comparison.png",
        "summary": "How the 10 countries differ — reach vs engagement, a country × category heat "
                   "matrix, an efficiency-quadrant scatter, and per-country trend lines.",
        "visuals": [
            ("Bar chart", "Total Views by country — raw reach ranking."),
            ("Line & clustered column", "Total Views (columns, left axis) vs Engagement Rate % "
                                        "(line, right axis) — separates *reach* from *quality* on dual axes."),
            ("Matrix (heatmap)", "Country × category with Avg Views per Video / Engagement Rate % / "
                                 "Trending Entries, conditionally colour-formatted to spot what each "
                                 "country over-indexes on."),
            ("Scatter", "Avg Views per Video (X) vs Engagement Rate % (Y), bubble per country — "
                        "four quadrants of high/low reach × high/low engagement."),
            ("Small multiples line", "Daily Views Trend, one mini panel per country, shared axis."),
        ],
        "slicers": [
            "**Country** — compare a subset (sync'd with the rest of the report).",
            "**Category** — see how the country comparison shifts within one category.",
        ],
        "tooltips": "Hovering a matrix cell or scatter bubble surfaces the underlying numbers "
                    "(avg views per video, engagement %, trending entries) for that country–category "
                    "combination — handy because the matrix itself only colours the cells.",
        "read": "A tall bar with a low engagement line = lots of views, weak engagement. The scatter's "
                "top-right quadrant is the sweet spot: high reach *and* high engagement. The small "
                "multiples reveal whether countries trend in sync or on their own cycles.",
    },
    "🏷️ Category & Content": {
        "file": "Category & Content.png",
        "summary": "What content performs — engagement and like/dislike by category, a treemap of "
                   "total views, and the view-size distribution of trending videos.",
        "visuals": [
            ("Bar chart", "Engagement Rate % by category — which categories punch above their view weight."),
            ("Bar chart", "Like / Dislike Ratio by category — audience sentiment per category."),
            ("Treemap", "Total Views by category — Music & Entertainment dominate the area."),
            ("Column histogram", "Trending Entries by `views_bucket` (< 100K, 100K–1M, 1M–5M, 5M–20M, 20M+)."),
        ],
        "slicers": [
            "**Country** — check a single country's category profile.",
            "**Views bucket** — isolate, say, only the 20M+ mega-viral videos and see which "
            "categories produce them.",
        ],
        "tooltips": "Hover a treemap tile or bar to see the precise Total Views / Engagement Rate % / "
                    "ratio for that category, rather than reading it off the axis.",
        "read": "Reach ≠ engagement: Music wins on raw views (treemap), but Nonprofits/Activism and "
                "Education top the *engagement* bar. The histogram shows most trending videos live in "
                "the 100K–1M band; 20M+ is rare.",
    },
    "📺 Channels & Top Videos": {
        "file": "Channels & Top Videos.png",
        "summary": "Who wins — top channels by views/engagement (with rank & data bars) and a "
                   "top-videos table with rendered thumbnails. The drill-through destination.",
        "visuals": [
            ("Channels table", "channel_title, Total Views, Unique Videos, Engagement Rate %, "
                               "Channel Rank — with data bars on engagement for quick scanning."),
            ("Top videos table", "Live **thumbnails** (`thumbnail_link` set to Image URL) + title, "
                                 "country, category, views, likes, engagement, days_to_trend. "
                                 "De-duplicated to one row per video."),
        ],
        "slicers": [
            "**Country / Category** — sync'd filters narrow both tables to a segment.",
            "**Top-N** — an optional field parameter to flip between Top 5 / 10 / 25 channels.",
        ],
        "tooltips": "Hovering a table row can trigger a **report-page tooltip** showing that video's "
                    "mini engagement stats; thumbnails preview the actual video frame inline.",
        "read": "This is the 'show me the videos behind the numbers' page. It's also the **drill-through "
                "target**: right-click any category or country on another page → *Drill through → "
                "Channels & Top Videos* to land here pre-filtered to that selection.",
    },
    "⏱️ Timing & Virality": {
        "file": "Timing & Virality.png",
        "summary": "When & how fast — a publish weekday × hour heatmap, a days-to-trend distribution, "
                   "average days-to-trend over time, and speed vs engagement.",
        "visuals": [
            ("Matrix heatmap", "Total Views by publish_weekday (rows) × publish_hour (columns), "
                               "colour-scaled — the best time of week to publish."),
            ("Card", "Avg Days to Trend (~7.6) and Median Days to Trend (~1)."),
            ("Histogram", "Trending Entries by `days_to_trend` (filtered ≤ 30 for readability) — "
                          "most videos trend within a day or two."),
            ("Line", "Avg Views per Video by Year-Month — momentum over the trending window."),
            ("Scatter", "Engagement Rate % vs days_to_trend — does trending fast mean more engagement?"),
        ],
        "slicers": [
            "**Country / Category** — see if the best publish time differs by market or content type.",
        ],
        "tooltips": "Hover a heatmap cell to read the exact Total Views for that weekday-and-hour slot; "
                    "hover histogram bars for the count of videos at each days-to-trend value.",
        "read": "The hot cells in the heatmap = publish windows that historically produced the most "
                "trending views. The long thin tail on the histogram is the handful of old videos that "
                "resurfaced (max ~4,215 days) — the median of ~1 day is the real story.",
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

# How the Power BI interactions work — shown on the home page.
INTERACTIONS = {
    "🔎 Slicers": "Every page has **slicers** (filter controls) for Country, Category, Year-Month and "
                  "View-bucket. They are **synced across all pages**, so selecting *Japan* on one page "
                  "keeps the whole report filtered to Japan as you navigate.",
    "🖱️ Cross-filtering": "Clicking a bar, treemap tile or map bubble **cross-filters** the other "
                          "visuals on the page to that selection. Click it again (or an empty area) to clear.",
    "💬 Tooltips": "Hovering any data point shows a **tooltip** with the exact underlying numbers. "
                   "Some visuals use a **report-page tooltip** — a mini dashboard that pops up on hover "
                   "with engagement stats for that item.",
    "🔗 Drill-through": "Right-click a category or country → **Drill through → Channels & Top Videos** "
                        "to jump to the detail page, automatically filtered to what you right-clicked.",
    "🧭 Navigation": "A **page navigator** (the buttons bottom-right of each page) moves between the "
                     "five pages without leaving the report.",
}

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


def render_page_detail(meta: dict):
    """Render the visuals / slicers / tooltips / how-to-read breakdown for a page."""
    left, right = st.columns(2)

    with left:
        st.markdown("#### 📈 Visuals on this page")
        for vtype, desc in meta["visuals"]:
            st.markdown(f"- **{vtype}** — {desc}")

    with right:
        st.markdown("#### 🔎 Slicers / filters")
        for s in meta["slicers"]:
            st.markdown(f"- {s}")

        st.markdown("#### 💬 Tooltips")
        st.markdown(meta["tooltips"])

    st.markdown("#### 🧭 How to read it")
    st.info(meta["read"])


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

    st.markdown("### 🕹️ How to interact with the dashboard")
    st.caption("These behaviours are built into the live Power BI report (and described per-page here).")
    for title, desc in INTERACTIONS.items():
        with st.expander(title, expanded=False):
            st.markdown(desc)

    st.markdown("### 📊 Dashboard Pages")
    st.caption("Use the sidebar to open each page with a full breakdown of its visuals, slicers and tooltips.")

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
    st.markdown("---")
    render_page_detail(meta)
