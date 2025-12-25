from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import uuid
from urllib.parse import urlparse
import os
import logging

# --------------------------
# Config
# --------------------------
app = Flask(__name__, static_folder=".", static_url_path="")
CORS(app)  # safe to have if you ever serve frontend separately

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kyc-boost-backend")

# Replace with the API you were using (kept as original)
BASE_URL = "https://zefame-free.com/api_free.php"
# Keep this configurable so you can rotate or set a fixed ID in env
DEVICE_ID = os.environ.get("DEVICE_ID", str(uuid.uuid4()))

HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "referer": "https://zefame.com/",
    "origin": "https://zefame.com"
}


# --------------------------
# Static / Frontend route
# --------------------------
@app.route("/")
def index():
    # Serves index.html from project root
    return send_from_directory(".", "index.html")


# --------------------------
# Helpers
# --------------------------
def extract_video_id(url: str):
    try:
        parsed = urlparse(url)
        for part in parsed.path.split("/"):
            if part.isdigit():
                return part
        # fallback: sometimes last path segment contains numbers before query
        last = parsed.path.rstrip("/").split("/")[-1]
        if last and any(c.isdigit() for c in last):
            return last.split("?")[0]
        return None
    except Exception as e:
        logger.exception("extract_video_id error")
        return None


def extract_username(url: str):
    try:
        parsed = urlparse(url)
        for part in parsed.path.split("/"):
            if part.startswith("@"):
                return part[1:]
        return None
    except Exception as e:
        logger.exception("extract_username error")
        return None


def place_order(service: int, link: str, extra: dict | None = None):
    payload = {
        "action": "order",
        "service": service,
        "link": link,
        "uuid": DEVICE_ID
    }
    if extra:
        payload.update(extra)

    try:
        resp = requests.post(BASE_URL, headers=HEADERS, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.exception("place_order request failed")
        return {"success": False, "error": str(e)}


# --------------------------
# Health
# --------------------------
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "device_id": DEVICE_ID})


# --------------------------
# API endpoints
# --------------------------
@app.route("/api/tiktok/views", methods=["POST"])
def tiktok_views():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    vid = extract_video_id(url)
    if not vid:
        return jsonify({"success": False, "error": "Invalid TikTok URL / could not extract video id"}), 400
    result = place_order(229, url, {"videoId": vid})
    return jsonify(result)


@app.route("/api/tiktok/likes", methods=["POST"])
def tiktok_likes():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    vid = extract_video_id(url)
    if not vid:
        return jsonify({"success": False, "error": "Invalid TikTok URL / could not extract video id"}), 400
    result = place_order(232, url, {"videoId": vid})
    return jsonify(result)


@app.route("/api/tiktok/followers", methods=["POST"])
def tiktok_followers():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    username = extract_username(url)
    if not username:
        return jsonify({"success": False, "error": "Invalid TikTok account URL / could not extract username"}), 400
    result = place_order(228, url, {"username": username})
    return jsonify(result)


@app.route("/api/instagram/views", methods=["POST"])
def instagram_views():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "Missing url"}), 400
    result = place_order(237, url)
    return jsonify(result)


@app.route("/api/youtube/views", methods=["POST"])
def youtube_views():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "Missing url"}), 400
    result = place_order(245, url)
    return jsonify(result)


@app.route("/api/twitter/views", methods=["POST"])
def twitter_views():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "Missing url"}), 400
    result = place_order(231, url)
    return jsonify(result)


@app.route("/api/facebook/boost", methods=["POST"])
def facebook_boost():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "Missing url"}), 400
    result = place_order(244, url, {"username": "share"})
    return jsonify(result)


@app.route("/api/telegram/views", methods=["POST"])
def telegram_views():
    payload = request.get_json(force=True, silent=True) or {}
    url = payload.get("url", "")
    if not url:
        return jsonify({"success": False, "error": "Missing url"}), 400
    result = place_order(248, url)
    return jsonify(result)


# --------------------------
# Run (development)
# --------------------------
if __name__ == "__main__":
    logger.info("Starting dev server...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
