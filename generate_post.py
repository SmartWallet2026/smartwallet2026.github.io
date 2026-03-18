import os, json, random, re, datetime, time, urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_URL  = "https://smartwallet2026.github.io"
POSTS_DIR = "posts"
TOPICS    = "post_topics.json"

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        raise SystemExit("GEMINI_API_KEY not set")
    print(f"Using API key starting with: {GEMINI_API_KEY[:8]}...")
    url = ("https://generativelanguage.googleapis.com/v1beta/models/"
           f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}")
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
    }).encode("utf-8")
    for attempt in range(4):
        try:
            req = urllib.request.Request(
                url, data=body,
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            err = e.read().decode("utf-8", errors="replace")
            print(f"HTTP {e.code}: {err[:300]}")
            if e.code == 429:
                wait = 30 * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"API error {e.code}: {err[:200]}")
    raise RuntimeError("Failed after 4 retries")

def main():
    with open(TOPICS, "r", encoding="utf-8") as f:
        data = json.load(f)
    pending = [t for t in data["topics"] if not t.get("published")]
    if not pending:
        print("All topics published!")
        return
    topic = random.choice(pending)
    print(f"Topic: {topic['title']}")
    prompt = f"Write a 500-word SEO blog post about '{topic['title']}'. Use h2 headings. Plain HTML body only."
    content = call_gemini(prompt)
    for t in data["topics"]:
        if t["slug"] == topic["slug"]:
            t["published"] = True
            t["published_date"] = datetime.date.today().isoformat()
    with open(TOPICS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.makedirs(POSTS_DIR, exist_ok=True)
    slug = topic["slug"]
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<title>{topic['title']} - SmartWallet</title></head><body>
<h1>{topic['title']}</h1>{content}
</body></html>"""
    with open(f"{POSTS_DIR}/{slug}.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done: posts/{slug}.html")

if __name__ == "__main__":
    main()
