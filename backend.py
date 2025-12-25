from flask import Flask, request, jsonify, send_from_directory
import requests
import uuid
from urllib.parse import urlparse
import os

app = Flask(__name__, static_folder=".", static_url_path="")

BASE_URL = "https://zefame-free.com/api_free.php"
DEVICE_ID = str(uuid.uuid4())

HEADERS = {
    "accept": "application/json",
    "user-agent": "Mozilla/5.0",
    "referer": "https://zefame.com/",
    "origin": "https://zefame.com"
}

# ================= FRONTEND =================

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# ================= HELPERS =================

def extract_video_id(url):
    parsed = urlparse(url)
    for part in parsed.path.split("/"):
        if part.isdigit():
            return part
    return None

def extract_username(url):
    parsed = urlparse(url)
    for part in parsed.path.split("/"):
        if part.startswith("@"):
            return part[1:]
    return None

def place_order(service, link, extra=None):
    data = {
        "action": "order",
        "service": service,
        "link": link,
        "uuid": DEVICE_ID
    }
    if extra:
        data.update(extra)

    r = requests.post(BASE_URL, headers=HEADERS, data=data)
    return r.json()

# ================= API =================

@app.route("/api/tiktok/views", methods=["POST"])
def tiktok_views():
    url = request.json.get("url")
    vid = extract_video_id(url)
    if not vid:
        return jsonify({"error": "Invalid TikTok URL"}), 400
    return jsonify(place_order(229, url, {"videoId": vid}))

@app.route("/api/tiktok/likes", methods=["POST"])
def tiktok_likes():
    url = request.json.get("url")
    vid = extract_video_id(url)
    if not vid:
        return jsonify({"error": "Invalid TikTok URL"}), 400
    return jsonify(place_order(232, url, {"videoId": vid}))

@app.route("/api/tiktok/followers", methods=["POST"])
def tiktok_followers():
    url = request.json.get("url")
    user = extract_username(url)
    if not user:
        return jsonify({"error": "Invalid account URL"}), 400
    return jsonify(place_order(228, url, {"username": user}))

@app.route("/api/instagram/views", methods=["POST"])
def instagram_views():
    return jsonify(place_order(237, request.json.get("url")))

@app.route("/api/youtube/views", methods=["POST"])
def youtube_views():
    return jsonify(place_order(245, request.json.get("url")))

@app.route("/api/twitter/views", methods=["POST"])
def twitter_views():
    return jsonify(place_order(231, request.json.get("url")))

@app.route("/api/facebook/boost", methods=["POST"])
def facebook_boost():
    return jsonify(place_order(244, request.json.get("url"), {"username": "share"}))

@app.route("/api/telegram/views", methods=["POST"])
def telegram_views():
    return jsonify(place_order(248, request.json.get("url")))

# ================= RUN =================

if __name__ == "__main__":
    app.run()