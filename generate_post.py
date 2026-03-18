#!/usr/bin/env python3
import os, json, random, re, datetime, time
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
POSTS_DIR = "posts"
TOPICS_FILE = "post_topics.json"

def call_gemini(prompt):
    if not GEMINI_API_KEY: raise RuntimeError("API Key missing")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    for attempt in range(5):
        try:
            return model.generate_content(prompt).text.strip()
        except Exception as e:
            if "429" in str(e):
                time.sleep(30 * (2 ** attempt))
            else: raise
    raise RuntimeError("Failed after retries")

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
    prompt = f"Write a simple HTML blog post for: {topic['title']}. Include only the body content."
    body = call_gemini(prompt)
    os.makedirs(POSTS_DIR, exist_ok=True)
    with open(os.path.join(POSTS_DIR, f"{topic['slug']}.html"), "w") as f: f.write(f"<html><body>{body}</body></html>")

if __name__ == "__main__": main()
