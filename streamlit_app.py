import os
import requests
from urllib.parse import urlencode

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env if present (local dev fallback)
load_dotenv()

# Prefer Streamlit secrets for deployment; fallback to environment variables
API_KEY = (
    st.secrets.get("YOUTUBE_API_KEY")
    if hasattr(st, "secrets") else None
)
if not API_KEY:
    API_KEY = os.getenv("YOUTUBE_API_KEY", "")
API_KEY = (API_KEY or "").strip()

DEFAULT_REGION = (
    st.secrets.get("REGION_CODE")
    if hasattr(st, "secrets") else None
)
if not DEFAULT_REGION:
    DEFAULT_REGION = os.getenv("REGION_CODE", "KR")
DEFAULT_REGION = (DEFAULT_REGION or "KR").strip() or "KR"
APP_VERSION = "0.2.0"

@st.cache_data(show_spinner=True, ttl=60 * 10)
def get_trending_videos(region: str):
    """Fetch top 30 trending videos for the given region using YouTube Data API v3."""
    base_url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "maxResults": 30,
        "regionCode": region,
        "key": API_KEY,
    }
    url = f"{base_url}?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "Unknown API error"))
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"네트워크 오류: {e}") from e

@st.cache_data(show_spinner=False, ttl=60 * 10)
def get_channel_stats(channel_ids):
    """Fetch channel statistics (subscriberCount) for a list of channel IDs.
    Returns dict[channelId] -> { 'subscriberCount': int | None }
    """
    if not channel_ids:
        return {}
    # Deduplicate and chunk if necessary (limit comfortably under URL length)
    unique_ids = list(dict.fromkeys([cid for cid in channel_ids if cid]))
    base_url = "https://www.googleapis.com/youtube/v3/channels"
    params = {
        "part": "statistics",
        "id": ",".join(unique_ids),
        "key": API_KEY,
    }
    url = f"{base_url}?{urlencode(params)}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            raise RuntimeError(data["error"].get("message", "Unknown API error"))
        result = {}
        for item in data.get("items", []):
            cid = item.get("id")
            stats = item.get("statistics", {})
            sub = stats.get("subscriberCount")
            try:
                sub_val = int(sub) if sub is not None else None
            except Exception:
                sub_val = None
            result[cid] = {"subscriberCount": sub_val}
        return result
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"채널 통계 조회 실패: {e}") from e

st.set_page_config(page_title="YouTube 트렌드", page_icon="📺", layout="wide")

st.title("📺 YouTube 인기 동영상")
st.caption("간단한 YouTube Data API v3 데모 · 썸네일 · 제목 · 채널명 · 조회수 · 30개 리스트")
st.sidebar.info(f"버전: v{APP_VERSION}")

# Country selection and refresh
# A concise list of common countries (can be extended)
COUNTRIES = [
    ("South Korea", "KR"), ("United States", "US"), ("Japan", "JP"), ("United Kingdom", "GB"), ("Germany", "DE"),
    ("France", "FR"), ("Canada", "CA"), ("Australia", "AU"), ("India", "IN"), ("Brazil", "BR"),
    ("Mexico", "MX"), ("Indonesia", "ID"), ("Russia", "RU"), ("Italy", "IT"), ("Spain", "ES"),
    ("Netherlands", "NL"), ("Sweden", "SE"), ("Norway", "NO"), ("Denmark", "DK"), ("Finland", "FI"),
    ("Poland", "PL"), ("Turkey", "TR"), ("Saudi Arabia", "SA"), ("United Arab Emirates", "AE"), ("South Africa", "ZA"),
    ("Thailand", "TH"), ("Vietnam", "VN"), ("Philippines", "PH"), ("Malaysia", "MY"), ("Singapore", "SG"),
    ("Hong Kong", "HK"), ("Taiwan", "TW"), ("Argentina", "AR"), ("Chile", "CL"), ("Colombia", "CO"),
    ("Peru", "PE"), ("Portugal", "PT"), ("Greece", "GR"), ("Ireland", "IE"), ("New Zealand", "NZ"),
    ("Belgium", "BE"), ("Austria", "AT"), ("Switzerland", "CH"), ("Czechia", "CZ"), ("Hungary", "HU"),
    ("Israel", "IL"), ("Egypt", "EG"), ("Nigeria", "NG"), ("Bangladesh", "BD"), ("Pakistan", "PK")
]

country_labels = [name for name, _ in COUNTRIES]
code_by_name = {name: code for name, code in COUNTRIES}

# Determine default index from DEFAULT_REGION
default_idx = 0
for i, (name, code) in enumerate(COUNTRIES):
    if code.upper() == (DEFAULT_REGION or "KR").upper():
        default_idx = i
        break

col1, col2 = st.columns([1, 6])
with col1:
    if st.button("🔄 새로고침", use_container_width=True):
        try:
            get_trending_videos.clear()  # type: ignore[name-defined]
        except Exception:
            pass
        try:
            get_channel_stats.clear()  # type: ignore[name-defined]
        except Exception:
            pass
        st.rerun()
with col2:
    selected_country = st.selectbox("지역 선택 (국가명)", country_labels, index=default_idx, help="국가명을 선택하면 해당 지역의 인기 동영상을 보여줍니다.")
    region_code = code_by_name.get(selected_country, DEFAULT_REGION).upper()

if not API_KEY:
    st.error("환경변수 YOUTUBE_API_KEY가 설정되지 않았습니다. .env 파일을 생성하고 API 키를 추가하세요.")
    st.stop()

# Fetch data with error handling
try:
    with st.spinner("인기 동영상을 불러오는 중..."):
        items = get_trending_videos(region_code)
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()

if not items:
    st.warning("표시할 동영상이 없습니다.")
    st.stop()

# Prepare channel stats lookup
channel_ids = []
for it in items:
    ch_id = it.get("snippet", {}).get("channelId")
    if ch_id:
        channel_ids.append(ch_id)
try:
    channel_stats_map = get_channel_stats(channel_ids)
except Exception as e:
    channel_stats_map = {}
    st.warning(f"채널 정보 일부를 불러오지 못했습니다: {e}")

# Render list of videos
for i, item in enumerate(items, start=1):
    snippet = item.get("snippet", {})
    stats = item.get("statistics", {})
    video_id = item.get("id")
    title = snippet.get("title", "(제목 없음)")
    channel = snippet.get("channelTitle", "(채널 정보 없음)")
    channel_id = snippet.get("channelId")
    thumbnails = snippet.get("thumbnails", {})
    thumb_url = (
        thumbnails.get("medium", {}).get("url")
        or thumbnails.get("high", {}).get("url")
        or thumbnails.get("default", {}).get("url")
    )
    views = stats.get("viewCount", "0")
    likes = stats.get("likeCount")
    comments = stats.get("commentCount")
    try:
        views_fmt = f"{int(views):,}회"
    except Exception:
        views_fmt = f"{views}회"
    try:
        likes_fmt = f"{int(likes):,}개" if likes is not None else "-"
    except Exception:
        likes_fmt = f"{likes}개" if likes is not None else "-"
    try:
        comments_fmt = f"{int(comments):,}개" if comments is not None else "-"
    except Exception:
        comments_fmt = f"{comments}개" if comments is not None else "-"

    subs_fmt = "-"
    if channel_id and channel_id in channel_stats_map:
        subs_val = channel_stats_map[channel_id].get("subscriberCount")
        if isinstance(subs_val, int):
            subs_fmt = f"{subs_val:,}명"

    video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else "#"

    with st.container(border=True):
        cols = st.columns([2, 6])
        with cols[0]:
            if thumb_url:
                st.image(thumb_url, use_container_width=True)
        with cols[1]:
            st.markdown(f"**{i}. [{title}]({video_url})**")
            st.write(f"채널: {channel} · 구독자: {subs_fmt}")
            st.write(f"조회수: {views_fmt} · 좋아요: {likes_fmt} · 댓글: {comments_fmt}")
