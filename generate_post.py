#!/usr/bin/env python3
import os, json, random, re, datetime, time, requests

SITE_URL = "https://smartwallet2026.github.io"
TOPICS_FILE = "post_topics.json"
POSTS_DIR = "posts"

def call_gemini(prompt):
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key: raise RuntimeError("API Key missing")
    
    # Debug: List models
    try:
        models_resp = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={key}")
        print(f"Models check: {models_resp.status_code}")
        if models_resp.status_code == 200:
            print("Available models logic...")
    except: pass

    for api_ver in ["v1", "v1beta"]:
        for model in ["gemini-1.5-flash", "gemini-pro", "gemini-1.0-pro"]:
            url = f"https://generativelanguage.googleapis.com/{api_ver}/models/{model}:generateContent?key={key}"
            try:
                resp = requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=60)
                if resp.status_code == 200:
                    return resp.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                print(f"Try {api_ver} {model}: {resp.status_code}")
            except: continue
    raise RuntimeError("All models failed")

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
    if not topic: return
    body = call_gemini(f"Write a div-wrapped HTML personal finance blog post for: {topic['title']}")
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(os.path.join(POSTS_DIR, f"{topic['slug']}.html"), "w") as f:
        f.write(f"<!DOCTYPE html><html><body>{body}</body></html>")

if __name__ == '__main__': main()
