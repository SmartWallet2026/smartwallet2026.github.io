import os, json, random, re, datetime, time, urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_URL  = "https://smartwallet2026.github.io"
POSTS_DIR = "posts"
TOPICS    = "post_topics.json"
MODEL     = "gemini-2.0-flash"

def call_gemini(prompt):
    if not GEMINI_API_KEY:
        raise SystemExit("GEMINI_API_KEY not set")
    print(f"API key prefix: {GEMINI_API_KEY[:8]}...")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{MODEL}:generateContent?key={GEMINI_API_KEY}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 2000}
    }).encode("utf-8")
    for attempt in range(5):
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
            print(f"HTTP {e.code}: {err[:200]}")
            if e.code == 429:
                wait = 60 * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s (attempt {attempt+1}/5)...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"API error {e.code}: {err[:200]}")
    raise RuntimeError("Failed after 5 retries")

def main():
    with open(TOPICS, "r", encoding="utf-8") as f:
        data = json.load(f)
    pending = [t for t in data["topics"] if not t.get("published")]
    if not pending:
        print("All topics published!")
        return
    topic = random.choice(pending)
    print(f"Topic: {topic['title']}")

    prompt = (
        f"Write a 600-word SEO personal finance blog post in English about: '{topic['title']}'. "
        "Use h2 headings and paragraphs. Return plain HTML body content only (no html/head/body tags). "
        "Do not include any markdown, code fences, or backticks — only raw HTML."
    )
    content = call_gemini(prompt)

    # Strip any accidental markdown code fences
    content = re.sub(r"^```(?:html)?\s*", "", content, flags=re.MULTILINE)
    content = re.sub(r"\s*```$", "", content, flags=re.MULTILINE).strip()

    for t in data["topics"]:
        if t["slug"] == topic["slug"]:
            t["published"] = True
            t["published_date"] = datetime.date.today().isoformat()
    with open(TOPICS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    os.makedirs(POSTS_DIR, exist_ok=True)
    slug = topic["slug"]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{topic['title']} - SmartWallet</title>
  <meta name="description" content="{topic.get('keyword','personal finance')} tips from SmartWallet">
  <link rel="canonical" href="https://smartwallet2026.github.io/posts/{slug}.html">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans&display=swap" rel="stylesheet">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-7508482110287286" crossorigin="anonymous"></script>
  <style>
    body{{font-family:'DM Sans',sans-serif;max-width:760px;margin:0 auto;padding:24px;line-height:1.7;color:#1a1a1a;background:#f8f8f6}}
    h1{{font-family:'Playfair Display',serif;font-size:2rem;margin:24px 0 12px;color:#085041}}
    h2{{font-family:'Playfair Display',serif;font-size:1.4rem;color:#085041;margin:32px 0 12px}}
    nav{{display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid #e8e8e8;margin-bottom:24px}}
    .logo{{font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#0F6E56;text-decoration:none}}
    p{{margin-bottom:16px}}
    footer{{margin-top:48px;padding-top:16px;border-top:1px solid #e8e8e8;color:#666;font-size:13px}}
  </style>
</head>
<body>
<nav>
  <a class="logo" href="/">SmartWallet</a>
  <div><a href="/about.html" style="color:#666;text-decoration:none">About</a></div>
</nav>
<article>
<h1>{topic['title']}</h1>
<p style="color:#666;font-size:13px">{datetime.date.today().strftime('%B %d, %Y')} &middot; {topic.get('category','Finance')}</p>
{content}
</article>
<footer>&copy; 2026 SmartWallet &middot; <a href="/privacy-policy.html">Privacy</a> &middot; <a href="/contact.html">Contact</a></footer>
</body>
</html>"""

    with open(f"{POSTS_DIR}/{slug}.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done: posts/{slug}.html")

if __name__ == "__main__":
    main()
