import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import subprocess

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

visited = set()


# =========================
# yt-dlp (meilleur fallback)
# =========================
def download(url):
    print(f"[DOWNLOAD PAGE MODE] {url}")

    subprocess.run([
        "yt-dlp",
        "-f", "best",
        "--referer", url,
        "--user-agent", "Mozilla/5.0",
        "--no-playlist",
        url
    ])


# =========================
# HTML VIDEO TAGS
# =========================
def extract_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    found = set()

    for tag in soup.find_all(["video", "source"]):
        src = tag.get("src")
        if src:
            found.add(urljoin(base_url, src))

    return found


# =========================
# REGEX GLOBAL (mp4 + m3u8 + js links)
# =========================
def extract_regex(html, base_url):
    found = set()

    matches = re.findall(
        r'(https?://[^\s"\']+\.(?:mp4|m3u8)|/[^\s"\']+\.(?:mp4|m3u8))',
        html
    )

    for m in matches:
        found.add(urljoin(base_url, m))

    return found


# =========================
# JAVASCRIPT PLAYER SRC
# =========================
def extract_js(html, base_url):
    found = set()

    matches = re.findall(
        r'src\s*:\s*["\'](.*?\.(?:mp4|m3u8))["\']',
        html
    )

    for m in matches:
        found.add(urljoin(base_url, m))

    return found


# =========================
# IFRAMES
# =========================
def extract_iframes(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for iframe in soup.find_all("iframe"):
        src = iframe.get("src")
        if src:
            links.append(urljoin(base_url, src))

    return links


# =========================
# MAIN CRAWLER
# =========================
def crawl(url, depth=0, max_depth=3):
    if url in visited or depth > max_depth:
        return

    visited.add(url)

    print(f"\n[SCAN] {url}")

    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        html = r.text
    except Exception as e:
        print("Erreur:", e)
        return

    # =========================
    # 1. extraction multi-source
    # =========================
    videos = set()

    videos |= extract_html(html, url)
    videos |= extract_regex(html, url)
    videos |= extract_js(html, url)

    # =========================
    # 2. si trouvé → download
    # =========================
    if videos:
        print("\n[Vidéos trouvées]\n")

        download(url)

        return

    # =========================
    # 3. iframe fallback
    # =========================
    print("[Aucun résultat → iframe]")

    for iframe_url in extract_iframes(html, url):
        print("[IFRAME]", iframe_url)
        crawl(iframe_url, depth + 1, max_depth)


# =========================
# START
# =========================
start_url = input("URL de départ : ")

crawl(start_url)