import pandas as pd
import json
import re
import os
import ftfy

BASE_DIR = "D:/POWERBI_Project"
OUTPUT   = os.path.join(BASE_DIR, "youtube_all_countries.csv")

# text columns that get whitespace-trimmed + mojibake-repaired
TEXT_COLS = ["title", "channel_title", "tags_clean", "description"]


def fix_text(val):
    """Repair latin1 mojibake (Ã©->é, emojis) and collapse whitespace."""
    s = ftfy.fix_text(str(val))
    s = re.sub(r"\s+", " ", s).strip()
    return s

# country code -> full country name
COUNTRIES = {
    "US": "United States",
    "GB": "United Kingdom",
    "CA": "Canada",
    "DE": "Germany",
    "FR": "France",
    "IN": "India",
    "JP": "Japan",
    "KR": "South Korea",
    "MX": "Mexico",
    "RU": "Russia",
}


def process_tags(raw):
    s = str(raw).strip()
    if s in ["[none]", "", "nan"]:
        return "", 0
    tags = re.findall(r'"([^"]+)"', s)
    if not tags:
        tags = [t.strip() for t in s.split("|") if t.strip()]
    return " | ".join(tags), len(tags)


def load_category_map(code):
    path = os.path.join(BASE_DIR, f"{code}_category_id.json")
    with open(path, "r", encoding="utf-8") as f:
        cat_data = json.load(f)
    return {item["id"]: item["snippet"]["title"] for item in cat_data["items"]}


def clean_country(code, country_name):
    csv_file = os.path.join(BASE_DIR, f"{code}videos.csv")
    print(f"\n=== {code} ({country_name}) ===")
    print("  Loading CSV...")
    df = pd.read_csv(
        csv_file,
        encoding="latin1",
        engine="c",
        quotechar='"',
        doublequote=False,
        escapechar="\\",
        on_bad_lines="skip",
    )
    print(f"  Rows: {df.shape[0]}  Cols: {df.shape[1]}")

    # --- country identity ---
    df["country_code"] = code
    df["country"] = country_name

    # --- dates ---
    df["trending_date"] = (
        pd.to_datetime(df["trending_date"], format="%y.%d.%m", errors="coerce")
        .dt.strftime("%Y-%m-%d")
    )
    pub = pd.to_datetime(df["publish_time"], errors="coerce", utc=True)
    df["publish_date"]    = pub.dt.strftime("%Y-%m-%d")
    df["publish_hour"]    = pub.dt.hour
    df["publish_weekday"] = pub.dt.day_name()
    df.drop(columns=["publish_time"], inplace=True)

    # --- category name from this country's JSON ---
    cat_map = load_category_map(code)
    df["category_name"] = df["category_id"].astype(str).map(cat_map).fillna("Unknown")

    # --- tags ---
    df[["tags_clean", "tag_count"]] = df["tags"].apply(
        lambda x: pd.Series(process_tags(x))
    )
    df.drop(columns=["tags"], inplace=True)

    # --- numerics ---
    for col in ["views", "likes", "dislikes", "comment_count"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    # --- derived metrics ---
    views_f    = df["views"].astype("float64").replace(0, float("nan"))
    dislikes_f = df["dislikes"].astype("float64").replace(0, float("nan"))
    df["engagement_rate"]    = ((df["likes"].astype("float64") + df["comment_count"].astype("float64")) / views_f).round(4)
    df["like_dislike_ratio"] = (df["likes"].astype("float64") / dislikes_f).round(2)
    # these ratios are NaN only when views=0 / dislikes=0 (valid videos, not missing data)
    df["engagement_rate"]    = df["engagement_rate"].fillna(0)
    df["like_dislike_ratio"] = df["like_dislike_ratio"].fillna(0)
    # tags column: missing tags should read as empty string, not null
    df["tags_clean"] = df["tags_clean"].fillna("")

    # --- drop any row that still has a null in any column ---
    before = len(df)
    df.dropna(inplace=True)
    dropped = before - len(df)
    print(f"  Dropped {dropped} null rows  ({dropped/before*100:.1f}%)  ->  {len(df)} remain")

    # --- flags -> 0/1 ---
    for col in ["comments_disabled", "ratings_disabled", "video_error_or_removed"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.upper().map({"TRUE": 1, "FALSE": 0}).fillna(0).astype(int)

    # --- text repair: fix mojibake (Ã©, emojis) + trim/collapse whitespace ---
    for col in TEXT_COLS:
        if col in df.columns:
            df[col] = df[col].apply(fix_text)
    # strip stray whitespace from key id/label columns too
    for col in ["video_id", "channel_title", "category_name", "country", "country_code"]:
        df[col] = df[col].astype(str).str.strip()

    # --- type fixes (no nulls remain, so safe to cast) ---
    df["publish_hour"] = df["publish_hour"].astype("int64")
    df["category_id"]  = df["category_id"].astype("int64")

    # --- logical sanity filters (drop impossible / removed records) ---
    n0 = len(df)
    df = df[df["views"] > 0]                                   # videos with 0 views are unusable
    df = df[df["likes"] <= df["views"]]                        # likes can't exceed views
    df = df[df["dislikes"] <= df["views"]]                     # dislikes can't exceed views
    df = df[df["comment_count"] <= df["views"]]               # comments can't exceed views
    df = df[df["video_error_or_removed"] == 0]                # drop deleted / errored videos
    df = df[df["trending_date"] >= df["publish_date"]]        # can't trend before publishing
    print(f"  Logical filters removed {n0 - len(df)} rows  ->  {len(df)} remain")

    # --- extra analytical columns ---
    # days from publish to trending (both are ISO date strings -> datetime)
    df["days_to_trend"] = (
        pd.to_datetime(df["trending_date"]) - pd.to_datetime(df["publish_date"])
    ).dt.days.astype("int64")
    # view-size bucket for distribution / histogram visuals
    df["views_bucket"] = pd.cut(
        df["views"],
        bins=[-1, 100_000, 1_000_000, 5_000_000, 20_000_000, float("inf")],
        labels=["< 100K", "100K - 1M", "1M - 5M", "5M - 20M", "20M +"],
    ).astype(str)

    # --- de-duplicate: one record per video per country per trending day ---
    n1 = len(df)
    df = df.drop_duplicates(subset=["video_id", "country_code", "trending_date"], keep="last")
    print(f"  Removed {n1 - len(df)} duplicate trending records  ->  {len(df)} remain")

    print(f"  Categories: {df['category_name'].nunique()}  | Unknown rows: {(df['category_name']=='Unknown').sum()}")
    return df


def main():
    frames = []
    for code, name in COUNTRIES.items():
        try:
            frames.append(clean_country(code, name))
        except Exception as e:
            print(f"  !! FAILED {code}: {e}")

    print("\nConcatenating all countries...")
    combined = pd.concat(frames, ignore_index=True)

    # final exact full-row duplicate sweep across the combined set
    n = len(combined)
    combined = combined.drop_duplicates(keep="first").reset_index(drop=True)
    print(f"Removed {n - len(combined)} exact duplicate rows from combined set")

    ordered = [
        "video_id", "title", "channel_title",
        "country_code", "country",
        "category_id", "category_name",
        "trending_date", "publish_date", "publish_hour", "publish_weekday",
        "days_to_trend",
        "views", "likes", "dislikes", "comment_count",
        "views_bucket",
        "engagement_rate", "like_dislike_ratio",
        "tags_clean", "tag_count",
        "thumbnail_link",
        "comments_disabled", "ratings_disabled", "video_error_or_removed",
        "description",
    ]
    combined = combined[[c for c in ordered if c in combined.columns]]

    # data-quality assertion: confirm zero nulls before saving
    nulls = combined.isna().sum().sum()
    print(f"\nNull check: {nulls} nulls remaining across all columns")

    combined.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"\nDone! Total rows: {combined.shape[0]}  Cols: {combined.shape[1]}  ->  {OUTPUT}")
    print("\nRows per country:")
    print(combined["country"].value_counts().to_string())
    print("\nFinal columns:")
    for c in combined.columns:
        print(f"  {c} ({combined[c].dtype})")


if __name__ == "__main__":
    main()
