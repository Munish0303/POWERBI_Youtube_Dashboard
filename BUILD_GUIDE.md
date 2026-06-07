# Power BI Build Guide — YouTube Trending (Global, 10 Countries)

Step-by-step instructions to build the 5-page advanced report from
`data/cleaned/youtube_all_countries.csv` (**342,656 rows**, all 10 countries).

> Table name used throughout: **`youtube_all_countries`** (matches the CSV / loaded query).
> `field` = a column; **Bold** = a Power BI button/menu.

---

## 0. SETUP (do this first)

### 0.1 Generate the data
```bash
pip install pandas ftfy
python cleaning_script/cleaning_all_countries.py
```
Produces `youtube_all_countries.csv` with these columns:
`video_id, title, channel_title, country_code, country, category_id, category_name,
trending_date, publish_date, publish_hour, publish_weekday, days_to_trend, views, likes,
dislikes, comment_count, views_bucket, engagement_rate, like_dislike_ratio, tags_clean,
tag_count, thumbnail_link, comments_disabled, ratings_disabled, video_error_or_removed, description`.

### 0.2 Load into Power BI
- **Home → Get data → Text/CSV** → select the CSV → **File Origin = 65001: Unicode (UTF-8)**
  (critical — keeps JP/KR/RU text correct) → **Transform Data**.
- Confirm types: dates → **Date**; views/likes/dislikes/comment_count/tag_count/publish_hour/
  days_to_trend/category_id → **Whole Number**; engagement_rate/like_dislike_ratio → **Decimal**;
  the rest → **Text**. Name the query `youtube_all_countries` → **Close & Apply**.

### 0.3 Column data categories & formatting
- `thumbnail_link` → **Column tools → Data category → Image URL** (tables show thumbnails).
- `engagement_rate` → **Format = Percentage**, 1 decimal.
- `publish_weekday` → sort by a weekday-number helper (see 0.4).
- `views_bucket` → sort by a bucket-order helper if you want `< 100K → 20M+` ordering.

### 0.4 Weekday sort helper (Modeling → New column)
```DAX
weekday_num =
SWITCH ( youtube_all_countries[publish_weekday],
    "Monday",1,"Tuesday",2,"Wednesday",3,"Thursday",4,
    "Friday",5,"Saturday",6,"Sunday",7 )
```
Then select `publish_weekday` → **Sort by column → weekday_num**.

### 0.5 Calendar table (Modeling → New table)
```DAX
Calendar =
ADDCOLUMNS (
    CALENDAR ( DATE(2017,11,1), DATE(2018,6,30) ),
    "Year", YEAR([Date]),
    "Month No", MONTH([Date]),
    "Month", FORMAT([Date],"MMM"),
    "Year-Month", FORMAT([Date],"YYYY-MM"),
    "Day Name", FORMAT([Date],"ddd"),
    "Weekday No", WEEKDAY([Date],2),
    "Is Weekend", IF(WEEKDAY([Date],2)>=6,"Weekend","Weekday")
)
```
- **Model view:** drag `Calendar[Date]` → `youtube_all_countries[trending_date]` (1-to-many, single).
- Select Calendar → **Table tools → Mark as date table → Date**.

### 0.6 Measures table
**Home → Enter data** → empty table `_Measures` → load. Put all measures below inside it.

---

## 1. DAX MEASURES (Modeling → New measure)

```DAX
Total Views      = SUM(youtube_all_countries[views])
Total Likes      = SUM(youtube_all_countries[likes])
Total Dislikes   = SUM(youtube_all_countries[dislikes])
Total Comments   = SUM(youtube_all_countries[comment_count])
Trending Entries = COUNTROWS(youtube_all_countries)
Unique Videos    = DISTINCTCOUNT(youtube_all_countries[video_id])
Unique Channels  = DISTINCTCOUNT(youtube_all_countries[channel_title])
Countries Covered= DISTINCTCOUNT(youtube_all_countries[country])
Avg Views per Video = DIVIDE([Total Views],[Unique Videos])

Engagement Rate % = DIVIDE([Total Likes]+[Total Comments],[Total Views])   -- format %
Like / Dislike Ratio = DIVIDE([Total Likes],[Total Dislikes])
Sentiment %       = DIVIDE([Total Likes],[Total Likes]+[Total Dislikes])   -- format %

Avg Days to Trend    = AVERAGE(youtube_all_countries[days_to_trend])
Median Days to Trend = MEDIAN(youtube_all_countries[days_to_trend])

Views 7D Moving Avg =
AVERAGEX(DATESINPERIOD('Calendar'[Date],MAX('Calendar'[Date]),-7,DAY),[Total Views])

Views MoM % =
VAR Cur=[Total Views]
VAR Prev=CALCULATE([Total Views],DATEADD('Calendar'[Date],-1,MONTH))
RETURN DIVIDE(Cur-Prev,Prev)

Channel Rank by Views =
RANKX(ALLSELECTED(youtube_all_countries[channel_title]),[Total Views],,DESC)

Views KPI Label =
VAR v=[Total Views]
RETURN SWITCH(TRUE(),
  v>=1E9,FORMAT(v/1E9,"0.0")&"B",
  v>=1E6,FORMAT(v/1E6,"0.0")&"M",
  v>=1E3,FORMAT(v/1E3,"0.0")&"K", FORMAT(v,"0"))

Selected Country Label =
IF(ISFILTERED(youtube_all_countries[country]),
  "Country: "&CONCATENATEX(VALUES(youtube_all_countries[country]),youtube_all_countries[country],", "),
  "All Countries")
```

---

## 2. PAGE 1 — OVERVIEW
1. **KPI cards (top row):** `Views KPI Label`, `Engagement Rate %`, `Countries Covered`,
   `Unique Channels`, `Unique Videos`. Add a card for `Selected Country Label` as a dynamic subtitle.
2. **Map:** Location = `country`, Bubble size = `Total Views`.
3. **Line:** X = `Calendar[Date]`, Y = `Total Views` **and** `Views 7D Moving Avg` (dash the avg line).
4. **Top categories:** bar — Axis `category_name`, Value `Total Views`, Top-N 10.
5. **Slicers:** `country`, `category_name`, `Calendar[Year-Month]`.

## 3. PAGE 2 — COUNTRY COMPARISON
1. **Bar:** `country` × `Total Views`.
2. **Line and clustered column:** X `country`, Column `Total Views`, Line `Engagement Rate %`
   (reach vs quality on dual axes).
3. **Matrix:** Rows `country`, Columns `category_name`, Values `Total Views` (or `Avg Views per Video`,
   `Engagement Rate %`) → **Cell elements → Background color = On** for a heatmap.
4. **Scatter:** X `Avg Views per Video`, Y `Engagement Rate %`, Legend `country`, Size `Trending Entries`;
   add **Analytics → Average lines** for quadrants.
5. **Small multiples line:** X `Calendar[Date]`, Y `Total Views`, Small multiples `country`
   (Markers off, shared Y-axis).

## 4. PAGE 3 — CATEGORY & CONTENT
1. **Bar:** `category_name` × `Engagement Rate %` (sorted desc).
2. **Bar:** `category_name` × `Like / Dislike Ratio`.
3. **Treemap:** Group `category_name`, Values `Total Views`.
4. **Column histogram:** Axis `views_bucket`, Value `Trending Entries`.
5. **Slicers:** `country`, `views_bucket`.

## 5. PAGE 4 — CHANNELS & TOP VIDEOS  (drill-through target)
1. **Channels table:** `channel_title`, `Total Views`, `Unique Videos`, `Engagement Rate %`,
   `Channel Rank by Views`. Top-N 25 by Total Views; add **data bars** on engagement.
2. **Top videos table:** `thumbnail_link` (Image URL), `title`, `country`, `category_name`,
   `views` (**Maximum** to avoid double-count), `likes`, `engagement_rate`, `days_to_trend`.
   - ⚠️ The same `video_id` trends on multiple days → keep only video-level columns + aggregated
     measures so rows collapse to **one per video** (don't include `trending_date`).
3. **Drill through:** Filters pane → Drill through → add `category_name` and `country`.

## 6. PAGE 5 — TIMING & VIRALITY
1. **Heatmap matrix:** Rows `publish_weekday` (sorted by `weekday_num`), Columns `publish_hour`,
   Values `Total Views` → conditional background color.
2. **Cards:** `Avg Days to Trend`, `Median Days to Trend`.
3. **Histogram:** Axis `days_to_trend` (bin size 1), Value `Trending Entries`; filter `days_to_trend ≤ 30`.
4. **Line:** X `Calendar[Year-Month]`, Y `Avg Views per Video` (or `Views MoM %`).
5. **Scatter:** X `days_to_trend`, Y `Engagement Rate %`.

---

## 7. FINISHING TOUCHES
- **Page navigator:** Insert → Buttons → **Navigator → Page navigator** (auto-labelled nav bar).
- **Sync slicers:** View → Sync slicers → sync `country` / `category_name` across all pages.
- **Bookmarks:** capture a "Clear filters" state → wire to a Reset button.
- **Top-N field parameter:** Modeling → New parameter → Numeric range 5–25 for dynamic Top-N.
- **Tooltip page:** hidden page (Allow use as tooltip = On) with mini engagement cards.
- **Theme:** View → Themes → apply one accent color for consistency.
- **Export:** File → Export → PDF, then refresh the images in `/screenshots`.

---

## ⚠️ Data-quality notes
- Use the **measures** (`Engagement Rate %`, `Like / Dislike Ratio`) for aggregation — never average
  the per-row `engagement_rate` (averaging ratios is wrong).
- `video_id` repeats across trending days → `Unique Videos` (distinct) vs `Trending Entries` (rows).
- ~3,400 rows are category **"Unknown"** (IDs missing from RU/KR/MX JSON) — filter out on category visuals if desired.
- `video_error_or_removed` is constant `0` (cleaning dropped errored videos) — nothing to chart.
- Trending window is **2017-11-14 → 2018-06-14**; the Calendar table matches it.
