# YouTube Trending Streamlit App

A minimal Streamlit app that displays the top 30 trending YouTube videos by region using the YouTube Data API v3. Shows thumbnail, title, channel name, and view count, with a refresh button and error handling.

## Features
- Thumbnail, Title, Channel, View Count
- Channel subscribers, Likes, Comment counts
- 30 items per page (YouTube mostPopular)
- Region selector (ISO 3166-1 alpha-2)
- Refresh button clears cache and reloads
- Basic error handling (missing API key, network/API errors)

## Quick Start
1. Create `.env` from `.env.example` and set your key
   ```env
   YOUTUBE_API_KEY=YOUR_API_KEY
   REGION_CODE=KR
   ```
2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app
   ```bash
   streamlit run streamlit_app.py
   ```

## Configuration
- The app prefers `st.secrets` from `.streamlit/secrets.toml` (for deployment) and falls back to environment variables (e.g., `.env`) for local development.
- `YOUTUBE_API_KEY` (required): YouTube Data API v3 key
- `REGION_CODE` (optional): Default region code (e.g., `KR`, `US`, `JP`). Can be changed in the UI.

### Using secrets (recommended for Streamlit Cloud)
Create `.streamlit/secrets.toml`:
```toml
YOUTUBE_API_KEY = "YOUR_API_KEY"
REGION_CODE = "KR"
```
On Streamlit Cloud, set these in the app's Secrets UI (same keys), no file commit needed.

## Versioning Policy
This project follows Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`.
- `MAJOR`: incompatible API changes or large UI/UX changes
- `MINOR`: backward-compatible functionality additions
- `PATCH`: backward-compatible bug fixes and small improvements

### Release Checklist
- Update version history in this README
- Manually test: load list, refresh, region input, error states
- If using Git, create a tag (optional):
  ```bash
  git add -A
  git commit -m "chore(release): vX.Y.Z"
  git tag vX.Y.Z
  git push origin main --tags
  ```

## Version History
- v0.2.0 — 2025-09-17
  - Feature: Show channel subscribers (via `channels.list`), likes, and comments
  - Chore: Refresh button clears both video and channel caches
- v0.1.1 — 2025-09-17
  - Fix: Markdown link formatting for video titles in `streamlit_app.py`
- v0.1.0 — 2025-09-17
  - Initial release: Trending list (30 items), thumbnails, titles, channels, view counts, refresh button, basic error handling, `.env` support

## Roadmap / Ideas
- Pagination or infinite scroll for more than 30 items
- Filters by category or keyword
- Open in modal with more metadata (likes, comments, publish date)
- Lightweight dark/light theme toggle
- Basic analytics (e.g., region switch usage)

## Troubleshooting
- Missing API key: Ensure `.env` exists with `YOUTUBE_API_KEY` set, then restart the app
- API quota errors: You may see the API error message from Google; try another key or wait for quota reset
- Network restrictions: Ensure `googleapis.com` is reachable over HTTPS

## Project Structure
```
ws_html_css_vibe/
├─ streamlit_app.py
├─ requirements.txt
├─ .env.example
└─ README.md
```
