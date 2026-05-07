import os
import sys
import json
import requests
import re
import time
from pathlib import Path
import argparse
import browser_cookie3
import json
import random

# ==== CONFIG ====
BASE_DIR = Path.cwd()  # CHANGE THIS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(SCRIPT_DIR, "user_cache.json") # this stores user ids for the story downloading since you need to use a session to fetch the user id and we want to cut down on total queries with a token.
# =================


# =================
# ALWAYS HAVE A VPN ON, AND WHEN YOU GET RATE LIMITED, JUST REFRESH
# =================
# https://scrapfly.io/blog/posts/how-to-scrape-instagram
# =================
# https://github.com/scrapfly/scrapfly-scrapers/tree/main/instagram-scraper
# =================

def load_cache():
    if not os.path.exists(CACHE_FILE):
        return {}
    
    try:
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}
    
def get_user_id_api(username, session=None):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-IG-App-ID": "936619743392459",
        "Accept": "application/json",
        "Referer": "https://www.instagram.com/",
    }

    res = requests.get(url, headers=headers)

    try:
        data = res.json()
    except:
        raise ValueError("API returned non-JSON")
    
    if "data" in data and "user" in data["data"]:
        print("API success (no session)")
        return data["data"]["user"]["id"]
    
    if session:
        print("API retry with session")
        res = session.get(url, headers=headers)
        data = res.json()

        if "data" in data and "user" in data["data"]:
            print("API seccess (with session)")
            return data["data"]["user"]["id"]

    raise ValueError(f"API failed: data")

def get_user_id_graphql(username):
    DOC_ID = "8759034877476257" #graphql working doc_id

    url = f"https://www.instagram.com/graphql/query/?doc_id={DOC_ID}&variables=%7B%22data%22%3A%7B%22count%22%3A12%2C%22include_relationship_info%22%3Atrue%2C%22latest_besties_reel_media%22%3Atrue%2C%22latest_reel_media%22%3Atrue%7D%2C%22username%22%3A%22{username}%22%2C%22__relay_internal__pv__PolarisIsLoggedInrelayprovider%22%3Atrue%2C%22__relay_internal__pv__PolarisFeedShareMenurelayprovider%22%3Atrue%7D"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    res = requests.get(url, headers=headers)
    res.raise_for_status()

    data = res.json()

    edges = data["data"]["xdt_api__v1__feed__user_timeline_graphql_connection"]["edges"]

    if not edges:
        raise ValueError("GraphQL failed: no posts (edges empty)")

    return edges[0]["node"]["user"]["id"]

def get_user_id(username, session=None):
    cache = load_cache()

    if username in cache:
        print("Used cached username.")
        return cache[username]
    
    #api
    try:
        user_id = get_user_id_api(username, session)
        print("UserID from API")
    except Exception as e:
        print("API failed:", e)

        try:
            user_id = get_user_id_graphql(username)
            print("User ID from GraphQL")
        except Exception as e:
            print("GraphQL failed:", e)

            try:
                url = f"https://www.instagram.com/{username}/"
                headers = {"User-Agent": "Mozilla/5.0"}

                res = requests.get(url, headers=headers)

                if '"profilePage_' not in res.text and session:
                    res = session.get(url, headers=headers)
                    print("Used session for HTML fallback")

                match = re.search(r'"profilePage_(\d+)"', res.text)
                if not match:
                    raise ValueError("HTML fallback failed")
                
                user_id = match.group(1)
                print("UserID from HTML")
            except Exception:
                raise ValueError("Could not resolve user_id")
    cache[username] = user_id
    save_cache(cache)
    return user_id

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def get_user_id_cached(username, session=None):
    cache = load_cache()

    if username in cache:
        print("Used cached username.")
        return cache[username]
    
    user_id = get_user_id(username, session)

    cache[username] = user_id
    print("Saving Username ID in cache.")
    save_cache(cache)

    return user_id

def download_photo(url, folder, index):
    ext = ".jpg"
    filename = f"{index:02d}{ext}"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"Already exists, skipping: {filename}")
        return

    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")

def download_video(url, folder, index):
    ext = ".mp4"
    filename = f"{index:02d}{ext}"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"Already exists, skipping: {filename}")
        return

    r = requests.get(url, stream=True)
    r.raise_for_status()
    print("Content-Type:", r.headers.get("Content-Type"))

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")

def download_story_photo(url, folder, story_id):
    ext = ".jpg"
    filename = f"{story_id} story{ext}"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"Already exists, skipping: {filename}")
        return

    r = requests.get(url, stream=True)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")

def download_story_video(url, folder, story_id):
    ext = ".mp4"
    filename = f"{story_id} story{ext}"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"Already exists, skipping: {filename}")
        return

    r = requests.get(url, stream=True)
    r.raise_for_status()
    print("Content-Type:", r.headers.get("Content-Type"))

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")

def download_reel(url, folder, username, reel_shortcode):
    ext = ".mp4"
    filename = f"{username} [{reel_shortcode}]{ext}"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        print(f"Already exists, skipping: {filename}")
        return

    r = requests.get(url, stream=True)
    r.raise_for_status()
    print("Content-Type:", r.headers.get("Content-Type"))

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    print(f"Downloaded: {filename}")

def handle_post(shortcode, session):
    DOC_ID = 8845758582119845 #if this expires, grab any post, throw it into the snapinsta private downloader and replace with a new doc id.

    query_url = f"https://www.instagram.com/graphql/query/?doc_id={DOC_ID}&variables=%7B%22shortcode%22%3A%22{shortcode}%22%2C%22fetch_tagged_user_count%22%3Anull%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    if session.is_private:
        queryql = session.get(query_url, stream=True, headers=headers)
    else:
        queryql = requests.get(query_url, stream=True, headers=headers)

    queryql.raise_for_status()

    data = queryql.json()

    media = data["data"]["xdt_shortcode_media"]

    edges = media.get("edge_sidecar_to_children", {}).get("edges", [])

    if not edges and media.get("is_video"):
        process_reel(media, data)
        return
    
    print("didnt work")

    shortcode = media["shortcode"]
    username = media["owner"]["username"]

    folder_name = f"{username} [{shortcode}]"
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    print(f"Saving to: {folder_path}")

    query_file = os.path.join(folder_path, f"{shortcode}_query.json")

    if os.path.exists(query_file):
        print(f"Query JSON already exists, skipping: {query_file}")
    else:
        with open(query_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved query JSON: {query_file}")

    # post date
    timestamp = media.get("taken_at_timestamp")
    post_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) if timestamp else None

    # caption
    caption_edges = media.get("edge_media_to_caption", {}).get("edges", [])
    caption = caption_edges[0]["node"]["text"] if caption_edges else None

    # location
    location = media.get("location", {}).get("name") if media.get("location") else None

    # Song
    music_info = media.get("clips_music_attribution_info")
    song = None
    if music_info:
        artist = music_info.get("artist_name")
        track = music_info.get("song_name")
        if artist or track:
            song = f"{artist} - {track}" if artist and track else artist or track
    
    info_data = {
        "username": username,
        "shortcode": shortcode,
        "post_date": post_date,
        "caption": caption,
        "location": location,
        "song": song
    }

    info_file = os.path.join(folder_path, f"{shortcode}_info.json")

    if os.path.exists(info_file):
        print(f"Info JSON already exists, skipping: {info_file}")
    else:
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info_data, f, indent=2, ensure_ascii=False)
        print(f"Saved info JSON: {info_file}")

    # Handle sidecar (carousel)

    if edges:
        expected_count = len(edges)
    else:
        expected_count = 1 #single post

    existing_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith((".jpg", ".mp4"))
    ]

    existing_count = len(existing_files)

    if existing_count == expected_count:
        print(f"All media already downloaded ({existing_count}/{expected_count}), skipping.")
        return

    if edges:
        for i, edge in enumerate(edges, start=1):
            node = edge["node"]

            # Highest resolution = last display_resource
            highest_res = node["display_resources"][-1]["src"]

            possible_video = node.get("video_url")

            if possible_video:
                download_video(possible_video, folder_path, i) # if has video in the node, grab the video instead of the thumbnail
            else:
                download_photo(highest_res, folder_path, i)

            if session.is_private:
                delay = random.uniform(8, 15)
                time.sleep(delay)
                print(f"{delay}s delay.")
            else:
                delay = random.uniform(2,4)
                time.sleep(delay)
                print(f"{delay}s delay.")

    else:
        if media.get("is_video"):
            video_url = media.get("video_url")

            if video_url:
                download_video(video_url, folder_path, 1)
            else:
                print("No video_url found (may need DASH parsing)")
        else:
            # Single image post fallback
            highest_res = media["display_resources"][-1]["src"]
            download_photo(highest_res, folder_path, 1)

        if session.is_private:
            delay = random.uniform(8, 15)
            time.sleep(delay)
            print(f"{delay}s delay.")
        else:
            delay = random.uniform(2,4)
            time.sleep(delay)
            print(f"{delay}s delay.")

    print("Done.")

def handle_story(story_username, session):
    QUERY_HASH = "de8017ee0a7c9c45ec4260733d81ea31"

    user_id = get_user_id_cached(story_username, session)

    query_url = (
        f"https://www.instagram.com/graphql/query/?query_hash={QUERY_HASH}&variables=%7B%22reel_ids%22%3A%5B{user_id}%5D%2C%22highlight_reel_ids%22%3A%5B%5D%2C%22precomposed_overlay%22%3Afalse%7D"
    ) # 

    # need session id for highlights as they require accounts. manually fetch the query and put into an "input_query.json" file in the same dir as dl.py

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    r = session.get(query_url, stream=True, headers=headers)
    r.raise_for_status()

    data = r.json()

    # input_file = os.path.join(BASE_DIR, "input_query.json")

    # with open(input_file, "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # 🔍 highlight structure
    reels = data["data"]["reels_media"]

    if not reels:
        print("No story data found")
        return

    story = reels[0]

    username = story["owner"]["username"]

    items = story.get("items", [])

    for item in items:
        story_id = item.get("id")
        print(story_id)

    folder_name = f"{username}'s Stories"
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    print(f"Saving story: {folder_path}")

    db_file = os.path.join(folder_path, "items.json")

    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            item_db = json.load(f)
    else:
        item_db = {}

    for item in items:
        try:
            item_id = str(item.get("id"))

            if not item_id:
                continue

            if item_id in item_db:
                print(f"Skipping existing item: {item_id}")
                continue
            
            info_file = os.path.join(folder_path, f"{item_id} info.json")

            # load existing if it exists (optional but nice)
            if os.path.exists(info_file):
                with open(info_file, "r", encoding="utf-8") as f:
                    existing_info = json.load(f)
            else:
                existing_info = {}

            timestamp = item.get("taken_at_timestamp")
            post_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) if timestamp else None

            # todo: add mobile api usage to get music from stories
            existing_info["username"] = username
            existing_info["story_id"] = str(story_id)
            existing_info["posted"] = post_date

            with open(info_file, "w", encoding="utf-8") as f:
                json.dump(existing_info, f, indent=2, ensure_ascii=False)

            print(f"Updated {story_id} info.json")

            is_video = item.get("is_video")

            if is_video:
                url = item.get("video_resources", [{}])[-1].get("src")
            else:
                url = item.get("display_resources", [{}])[-1].get("src")

            if not url:
                continue

            if is_video:
                download_story_video(url, folder_path, item_id)
            else:
                download_story_photo(url, folder_path, item_id)

            timestamp = item.get("taken_at_timestamp")
            readable_time = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                if timestamp else None
            )

            item_db[item_id] = {
                "type": "video" if is_video else "image",
                "url": url,
                "filename": item_id,
                "timestamp": timestamp,
                "datetime": readable_time
            }

            if session.is_private:
                delay = random.uniform(8, 15)
                time.sleep(delay)
                print(f"{delay}s delay.")
            else:
                delay = random.uniform(2,4)
                time.sleep(delay)
                print(f"{delay}s delay.")
            
        except Exception as e:
            print(f"Error processing item: {e}")

            with open(db_file, "w", encoding="utf-8") as f:
                json.dump(item_db, f, indent=2, ensure_ascii=False)
            
            print("Progress saved after error, continuing...")
            continue

    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(item_db, f, indent=2, ensure_ascii=False)
    
    print("Story sync complete")

def handle_highlight(highlight_id, session):
    QUERY_HASH = "de8017ee0a7c9c45ec4260733d81ea31"

    query_url = (
        f"https://www.instagram.com/graphql/query/?query_hash={QUERY_HASH}&variables=%7B%22reel_ids%22%3A%5B%5D%2C%22highlight_reel_ids%22%3A%5B{highlight_id}%5D%2C%22precomposed_overlay%22%3Afalse%7D"
    )

    # need session id for highlights as they require accounts. manually fetch the query and put into an "input_query.json" file in the same dir as dl.py

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    r = session.get(query_url, stream=True, headers=headers)
    r.raise_for_status()

    data = r.json()

    # input_file = os.path.join(BASE_DIR, "input_query.json")

    #with open(input_file, "r", encoding="utf-8") as f:
    #    data = json.load(f)

    # 🔍 highlight structure
    reels = data["data"]["reels_media"]

    if not reels:
        print("No highlight data found")
        return

    highlight = reels[0]

    title = highlight.get("title")
    username = highlight["owner"]["username"]

    folder_name = f"{username} [highlight {highlight_id}]"
    folder_path = os.path.join(BASE_DIR, folder_name)
    os.makedirs(folder_path, exist_ok=True)

    print(f"Saving highlight: {title} -> {folder_path}")

    items = highlight.get("items", [])

    info_file = os.path.join(folder_path, "info.json")

    # load existing if it exists (optional but nice)
    if os.path.exists(info_file):
        with open(info_file, "r", encoding="utf-8") as f:
            existing_info = json.load(f)
    else:
        existing_info = {}  

    if "title" not in existing_info:
        existing_info["title"] = None

    existing_info["username"] = username
    existing_info["highlight_id"] = str(highlight_id)
    existing_info["total_items"] = len(items)
    existing_info["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")

    with open(info_file, "w", encoding="utf-8") as f:
        json.dump(existing_info, f, indent=2, ensure_ascii=False)

    print("Updated info.json")

    db_file = os.path.join(folder_path, "items.json")

    if os.path.exists(db_file):
        with open(db_file, "r", encoding="utf-8") as f:
            item_db = json.load(f)
    else:
        item_db = {}

    for item in items:
        try:
            item_id = item.get("id")

            if not item_id:
                continue

            if item_id in item_db:
                print(f"Skipping existing item: {item_id}")
                continue

            is_video = item.get("is_video")

            if is_video:
                url = item.get("video_resources", [{}])[-1].get("src")
                ext = ".mp4"
            else:
                url = item.get("display_resources", [{}])[-1].get("src")
                ext = ".jpg"

            if not url:
                continue
    
            existing_files = [
                f for f in os.listdir(folder_path)
                if f.lower().endswith((".jpg", ".mp4"))
            ]
            next_index = len(existing_files) + 1

            filename = f"{next_index:02d}{ext}"

            if is_video:
                download_video(url, folder_path, next_index)
            else:
                download_photo(url, folder_path, next_index)

            timestamp = item.get("taken_at_timestamp")
            readable_time = (
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
                if timestamp else None
            )

            item_db[item_id] = {
                "type": "video" if is_video else "image",
                "url": url,
                "filename": filename,
                "timestamp": timestamp,
                "datetime": readable_time
            }

            if session.is_private:
                delay = random.uniform(8, 15)
                time.sleep(delay)
                print(f"{delay}s delay.")
            else:
                delay = random.uniform(2,4)
                time.sleep(delay)
                print(f"{delay}s delay.")

        except Exception as e:
            print(f"Error processing item: {e}")

            with open(db_file, "w", encoding="utf-8") as f:
                json.dump(item_db, f, indent=2, ensure_ascii=False)
            
            print("Progress saved after error, continuing...")
            continue

    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(item_db, f, indent=2, ensure_ascii=False)
    
    print("Highlight sync complete")

def handle_reel(reel_shortcode, session):
    DOC_ID = 8845758582119845 #if this expires, grab any post, throw it into the snapinsta private downloader and replace with a new doc id.

    query_url = f"https://www.instagram.com/graphql/query/?doc_id={DOC_ID}&variables=%7B%22shortcode%22%3A%22{reel_shortcode}%22%2C%22fetch_tagged_user_count%22%3Anull%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D"
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest",
    }

    if session.is_private:
        queryql = session.get(query_url, stream=True, headers=headers)
    else:
        queryql = requests.get(query_url, stream=True, headers=headers)

    queryql.raise_for_status()

    data = queryql.json()

    #https://www.instagram.com/graphql/query/?doc_id=8845758582119845&variables=%7B%22shortcode%22%3A%22DWREVncD_Zx%22%2C%22fetch_tagged_user_count%22%3Anull%2C%22hoisted_comment_id%22%3Anull%2C%22hoisted_reply_id%22%3Anull%7D

    media = data["data"]["xdt_shortcode_media"]

    process_reel(media, data, session)

def process_reel(media, data, session):
    shortcode = media["shortcode"]
    username = media["owner"]["username"]

    reels_folder = "reels"
    data_folder = "data"
    reels_path = os.path.join(BASE_DIR, reels_folder)
    reels_data = os.path.join(reels_folder, data_folder)

    if not os.path.exists(reels_folder):
        os.makedirs(reels_path, exist_ok=True)

    if not os.path.exists(reels_data):
        os.makedirs(reels_data, exist_ok=True)

    print(f"Saving to: {reels_path}")

    query_file = os.path.join(reels_data, f"{shortcode}_query.json")

    if os.path.exists(query_file):
        print(f"Query JSON already exists, skipping: {query_file}")
    else:
        with open(query_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Saved query JSON: {query_file}")

    # post date
    timestamp = media.get("taken_at_timestamp")
    post_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp)) if timestamp else None

    # caption
    caption_edges = media.get("edge_media_to_caption", {}).get("edges", [])
    caption = caption_edges[0]["node"]["text"] if caption_edges else None

    # location
    location = media.get("location", {}).get("name") if media.get("location") else None

    # Song
    music_info = media.get("clips_music_attribution_info")
    song = None
    if music_info:
        artist = music_info.get("artist_name")
        track = music_info.get("song_name")
        if artist or track:
            song = f"{artist} - {track}" if artist and track else artist or track
    
    info_data = {
        "username": username,
        "shortcode": shortcode,
        "post_date": post_date,
        "caption": caption,
        "location": location,
        "song": song
    }

    info_file = os.path.join(reels_data, f"{shortcode}_info.json")

    if os.path.exists(info_file):
        print(f"Info JSON already exists, skipping: {info_file}")
    else:
        with open(info_file, "w", encoding="utf-8") as f:
            json.dump(info_data, f, indent=2, ensure_ascii=False)
        print(f"Saved info JSON: {info_file}")

    # Handle sidecar (carousel)
    edges = media.get("edge_sidecar_to_children", {}).get("edges", [])

    video_filename = f"{username} [{shortcode}].mp4"
    video_path = os.path.join(reels_path, video_filename)

    if os.path.exists(video_path):
        print(f"Reel already exists, skipping: {video_filename}")
        return

    if edges:
        for i, edge in enumerate(edges, start=1):
            node = edge["node"]

            # Highest resolution = last display_resource
            highest_res = node["display_resources"][-1]["src"]

            possible_video = node.get("video_url")

            if possible_video:
                download_reel(possible_video, reels_path, username, shortcode) # if has video in the node, grab the video instead of the thumbnail
            else:
                download_photo(highest_res, reels_path, i)

            if session.is_private:
                delay = random.uniform(8, 15)
                time.sleep(delay)
                print(f"{delay}s delay.")
            else:
                delay = random.uniform(2,4)
                time.sleep(delay)
                print(f"{delay}s delay.")
    else:
        if media.get("is_video"):
            video_url = media.get("video_url")

            if video_url:
                download_reel(video_url, reels_path, username, shortcode)
            else:
                print("No video_url found (may need DASH parsing)")
        else:
            # Single image post fallback
            highest_res = media["display_resources"][-1]["src"]
            download_photo(highest_res, reels_path, 1)

        if session.is_private:
            delay = random.uniform(8, 15)
            time.sleep(delay)
            print(f"{delay}s delay.")
        else:
            delay = random.uniform(2,4)
            time.sleep(delay)
            print(f"{delay}s delay.")

    print("Done.")

def get_session(use_private=False):
    session = requests.Session()

    if use_private:
        try:
            cookies = browser_cookie3.firefox(domain_name=".instagram.com")
            session.cookies.update(cookies)
        except Exception as e:
            print("Could not load cookies:", e)
            print("Try closing Chrome or using Firefox")

    session.is_private = use_private
    return session

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--private", action="store_true")
    parser.add_argument("post_url")

    args = parser.parse_args()

    post_url = args.post_url
    use_private = args.private


    session = get_session(use_private)

    post_pattern = r"instagram\.com/p/([A-Za-z0-9_-]+)"
    highlight_pattern = r"instagram\.com/stories/highlights/(\d+)"
    reel_pattern = r"instagram\.com/reel?/([A-Za-z0-9_-]+)"
    story_pattern = r"instagram\.com/stories/([A-Za-z0-9._-]+)"

    post_match = re.search(post_pattern, post_url)
    highlight_match = re.search(highlight_pattern, post_url)
    reel_match = re.search(reel_pattern, post_url)
    story_match = re.search(story_pattern, post_url)

    if post_match:
        shortcode = post_match.group(1)
        print("Detected POST:", shortcode)
        handle_post(shortcode, session)
    elif highlight_match:
        highlight_id = highlight_match.group(1)
        highlight_id = int(highlight_id)
        handle_highlight(highlight_id, session)
    elif reel_match:
        reel_shortcode = reel_match.group(1)
        print("Detected Reel:", reel_shortcode)
        handle_reel(reel_shortcode, session)
    elif story_match:
        story_username = story_match.group(1)
        print("Detected Story:", story_username)
        handle_story(story_username, session)
    else:
        print("Unsupported URL")

if __name__ == "__main__":
    main()