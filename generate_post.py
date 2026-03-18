#!/usr/bin/env python3
import os, json, random, re, datetime, time, requests

SITE_URL = "https://smartwallet2026.github.io"
TOPICS_FILE = "post_topics.json"
POSTS_DIR = "posts"

def call_gemini(prompt):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key: raise RuntimeError("API Key missing")
    # Try both v1 and v1beta endpoints
    for api_ver in ["v1", "v1beta"]:
        url = f"https://generativelanguage.googleapis.com/{api_ver}/models/gemini-1.5-flash:generateContent?key={key}"
        try:
            resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
            if resp.status_code == 200:
                return resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
            print(f"API {api_ver} failed: {resp.status_code} {resp.text}")
        except Exception as e:
            print(f"Request failed: {e}")
    raise RuntimeError("All API attempts failed")

def pick_topic():
    if not os.path.exists(TOPICS_FILE): return None
    with open(TOPICS_FILE, "r") as f: data = json.load(f)
    pending = [t for t in data["topics"] if not t.get("published")]
    if not pending: return None
    topic = random.choice(pending)
    for t in data["topics"]:
        if t["slug"] == topic["slug"]:
            t["published"] = True
            t["published_date"] = datetime.date.today().isoformat()
    with open(TOPICS_FILE, "w") as f: json.dump(data, f, indent=2)
    return topic

def main():
    topic = pick_topic()
    if not topic:
        print("No topics found")
        return
    print(f"Generating for: {topic['title']}")
    prompt = f"Write a simple HTML blog post for: {topic['title']}. Keyword: {topic['keyword']}. Include only the body content inside a <div>."
    body = call_gemini(prompt)
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(os.path.join(POSTS_DIR, f"{topic['slug']}.html"), "w") as f:
        f.write(f"<!DOCTYPE html><html><body>{body}</body></html>")
    print("Done")

if __name__ == '__main__': main()
