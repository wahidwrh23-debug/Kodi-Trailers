import os
import subprocess
import time
import urllib.request
import re
import html

ROOT = "./PreShow_Trailers"
HISTORY_FILE = "./history_ids.txt"
TAGS_FILE = "./history_tags.txt"

CHANNELS_YTDLP = ["@FandangoMovieclips", "@tseries", "@DharmaMovies", "@RapiFilms", "@WellGoUSA"]
RSS_FEEDS = ["https://www.youtube.com/feeds/videos.xml?user=WarnerBrosPictures", "https://www.youtube.com/feeds/videos.xml?channel_id=UC2-VHbcGqGxNRUv0YIekMkA"]

if not os.path.exists(ROOT): os.makedirs(ROOT)
if not os.path.exists(HISTORY_FILE): open(HISTORY_FILE, 'w').close()
if not os.path.exists(TAGS_FILE): open(TAGS_FILE, 'w').close()

def github_robot_sniper():
    print("🚀 GITHUB ROBOT: 30-DAY FRESHNESS SCAN...\n")
    with open(HISTORY_FILE, 'r') as f: history = [line.strip() for line in f if line.strip()]
    with open(TAGS_FILE, 'r') as f: downloaded_tags = [line.strip() for line in f if line.strip()]
    new_count = 0
    junk = ["THIS WEEK", "COMPILATION", "MASHUP", "OFFICIAL VIDEO", "SONG", "LYRICAL", "MUSIC VIDEO", "EPISODE", "K-DRAMA", "TV SERIES", "FAN MADE", "JUKEBOX", "AUDIO", "REVIEW"]

    for handle in CHANNELS_YTDLP:
        print(f"📡 Scanning: {handle}...")
        cmd = ['yt-dlp', '--flat-playlist', '--playlist-end', '50', '--dateafter', 'today-30days', '--print', '%(title)s|||%(id)s', '--extractor-args', 'youtube:player_client=web', f'https://www.youtube.com/{handle}/videos']
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode('utf-8', errors='ignore').splitlines()
            for line in output:
                if '|||' not in line: continue
                title, vid_id = line.split('|||', 1)
                title = title.upper()
                if vid_id in history: continue
                if any(x in title for x in ["TRAILER", "TEASER", "GLIMPSE", "4K", "OFFICIAL"]) and not any(j in title for j in junk):
                    movie_tag = title.split(' ')[0].strip('[]()#')
                    if not any(movie_tag in existing for existing in downloaded_tags):
                        clean_name = "".join([c for c in title[:50] if c.isalnum() or c in " -()"]).strip()
                        with open(os.path.join(ROOT, f"{clean_name}.strm"), "w", encoding="utf-8") as f: f.write(f"plugin://plugin.video.youtube/play/?video_id={vid_id}")
                        with open(HISTORY_FILE, 'a') as h: h.write(vid_id + "\n")
                        with open(TAGS_FILE, 'a') as t: t.write(movie_tag + "\n")
                        print(f"   ✅ ADDED: {clean_name}")
                        downloaded_tags.append(movie_tag)
                        new_count += 1
        except Exception: print(f"   🚨 ERROR on {handle}")

    for url in RSS_FEEDS:
        name = "Warner Bros" if "WarnerBros" in url else "BASE"
        print(f"📡 Ghosting: {name}...")
        try:
            feed = urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})).read().decode('utf-8')
            for entry in feed.split('<entry>')[1:]:
                title = html.unescape(re.search(r'<title>(.*?)</title>', entry).group(1)).upper()
                vid_id = re.search(r'<yt:videoId>(.*?)</yt:videoId>', entry).group(1)
                if vid_id in history: continue
                if any(x in title for x in ["TRAILER", "TEASER", "GLIMPSE", "4K", "OFFICIAL"]) and not any(j in title for j in junk):
                    movie_tag = title.split(' ')[0].strip('[]()#')
                    if not any(movie_tag in existing for existing in downloaded_tags):
                        clean_name = "".join([c for c in title[:50] if c.isalnum() or c in " -()"]).strip()
                        with open(os.path.join(ROOT, f"{clean_name}.strm"), "w", encoding="utf-8") as f: f.write(f"plugin://plugin.video.youtube/play/?video_id={vid_id}")
                        with open(HISTORY_FILE, 'a') as h: h.write(vid_id + "\n")
                        with open(TAGS_FILE, 'a') as t: t.write(movie_tag + "\n")
                        print(f"   ✅ ADDED: {clean_name}")
                        downloaded_tags.append(movie_tag)
                        new_count += 1
        except Exception: print(f"   🚨 FEED ERROR on {name}")
    print(f"\n✨ DONE. {new_count} trailers added.")

if __name__ == "__main__": github_robot_sniper()
