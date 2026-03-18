import os, json, random, re, datetime, time, urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_URL  = "https://smartwallet2026.github.io"
AUTHOR    = "Alex Morgan"
ADSENSE_ID= "ca-pub-7508482110287286"
POSTS_DIR = "posts"
TOPICS    = "post_topics.json"

def call_gemini(prompt):
    """Call Gemini REST API using API key in URL (no Authorization header)."""
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 3000}
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
            body2 = e.read().decode("utf-8", errors="replace")
            if e.code == 429:
                wait = 30 * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s (attempt {attempt+1}/4)...")
                time.sleep(wait)
            else:
                raise RuntimeError(f"Gemini API error {e.code}: {body2[:300]}")
    raise RuntimeError("Gemini API failed after 4 retries")

def pick_topic():
    with open(TOPICS, "r", encoding="utf-8") as f:
        data = json.load(f)
    pending = [t for t in data["topics"] if not t.get("published")]
    if not pending:
        print("All topics published!")
        return None
    topic = random.choice(pending)
    for t in data["topics"]:
        if t["slug"] == topic["slug"]:
            t["published"] = True
            t["published_date"] = datetime.date.today().isoformat()
    with open(TOPICS, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return topic

def generate_content(topic):
    prompt = f"""Write a SEO-optimized personal finance blog article.
TOPIC: {topic['title']}
KEYWORD: {topic['keyword']}
CATEGORY: {topic['category']}
Rules: 800-1000 words, 5 H2 sections, actionable tips.
Output ONLY valid JSON (no markdown fences):
{{"title":"...","meta_description":"...","intro":"...","sections":[{{"heading":"...","content":"..."}}],"conclusion":"...","read_time":"X min read"}}"""
    raw = call_gemini(prompt)
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw.strip())
    return json.loads(raw)

def build_html(topic, post):
    today = datetime.date.today()
    slug  = topic["slug"]
    url   = f"{SITE_URL}/posts/{slug}.html"
    img   = f"https://images.unsplash.com/{topic.get('image','photo-1579621970563-ebec7560ff3e')}?w=1200&q=80"
    secs  = ""
    for s in post.get("sections", []):
        ps = "".join(f"<p>{p.strip()}</p>" for p in s["content"].split("\n") if p.strip())
        secs += f"<h2>{s['heading']}</h2>\n{ps}\n"
    intro = "".join(f"<p>{p.strip()}</p>" for p in post["intro"].split("\n") if p.strip())
    concl = "".join(f"<p>{p.strip()}</p>" for p in post["conclusion"].split("\n") if p.strip())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{post['meta_description']}">
  <meta name="robots" content="index,follow">
  <title>{post['title']} - SmartWallet</title>
  <link rel="canonical" href="{url}">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--g:#0F6E56;--gd:#085041;--bg:#f8f8f6;--mu:#666;--bd:#e8e8e8}}
    body{{font-family:"DM Sans",sans-serif;background:var(--bg);color:#1a1a1a;line-height:1.7}}
    a{{text-decoration:none;color:inherit}}
    nav{{background:#fff;border-bottom:1px solid var(--bd);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100}}
    .logo{{font-family:"Playfair Display",serif;font-size:22px;font-weight:700}}.logo span{{color:var(--g)}}
    .hi{{width:100%;max-height:380px;object-fit:cover;display:block}}
    .aw{{max-width:760px;margin:0 auto;padding:24px}}
    h1{{font-family:"Playfair Display",serif;font-size:32px;font-weight:700;line-height:1.3;margin:20px 0 12px}}
    .meta{{font-size:13px;color:var(--mu);margin-bottom:32px;padding-bottom:20px;border-bottom:1px solid var(--bd)}}
    .ab{{font-size:17px;line-height:1.85}}.ab p{{margin-bottom:20px}}.ab h2{{font-family:"Playfair Display",serif;font-size:24px;color:var(--gd);margin:36px 0 14px}}
    .cta{{background:var(--gd);color:#fff;border-radius:12px;padding:32px;text-align:center;margin:40px 0}}
    .cta h3{{font-family:"Playfair Display",serif;font-size:22px;margin-bottom:8px}}
    footer{{background:#fff;border-top:1px solid var(--bd);padding:20px 40px;display:flex;justify-content:space-between;align-items:center;margin-top:40px;font-size:13px;color:var(--mu)}}
    .fl{{display:flex;gap:20px;list-style:none}}.fl a:hover{{color:var(--g)}}
  </style>
</head>
<body>
<nav><a class="logo" href="/">Smart<span>Wallet</span></a>
  <ul style="display:flex;gap:24px;list-style:none;font-size:14px;color:var(--mu)">
    <li><a href="/">Home</a></li><li><a href="/about.html">About</a></li>
  </ul>
</nav>
<img class="hi" src="{img}" alt="{post['title']}">
<div class="aw">
  <p style="font-size:13px;color:var(--g);margin-top:16px">{topic['category'].upper()}</p>
  <h1>{post['title']}</h1>
  <p class="meta">{AUTHOR} &nbsp;&middot;&nbsp; {today.strftime('%B %d, %Y')} &nbsp;&middot;&nbsp; {post.get('read_time','7 min read')}</p>
  <div class="ab">{intro}{secs}<h2>Final Thoughts</h2>{concl}</div>
  <div class="cta">
    <h3>Get Smarter With Money</h3>
    <p style="color:#9FE1CB;margin:8px 0 20px">Weekly tips &mdash; free, no spam.</p>
    <div style="display:flex;gap:10px;justify-content:center;max-width:380px;margin:0 auto">
      <input type="email" placeholder="Your email" style="flex:1;padding:10px;border-radius:8px;border:none">
      <button style="background:#5DCAA5;color:#085041;border:none;padding:10px 20px;border-radius:8px;font-weight:600;cursor:pointer">Subscribe</button>
    </div>
  </div>
</div>
<footer>
  <b>SmartWallet</b>
  <ul class="fl"><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/about.html">About</a></li><li><a href="/contact.html">Contact</a></li></ul>
  <span>&copy; 2026 SmartWallet</span>
</footer>
</body></html>"""

def main():
    if not GEMINI_API_KEY:
        raise SystemExit("ERROR: GEMINI_API_KEY not set")
    print(f"API key: {GEMINI_API_KEY[:8]}...")
    topic = pick_topic()
    if not topic:
        return
    print(f"Generating: {topic['title']}")
    post  = generate_content(topic)
    html  = build_html(topic, post)
    os.makedirs(POSTS_DIR, exist_ok=True)
    path  = os.path.join(POSTS_DIR, f"{topic['slug']}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Done: {path}")

if __name__ == "__main__":
    main()
