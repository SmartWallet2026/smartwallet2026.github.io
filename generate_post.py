import os, json, random, re, datetime, time
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_URL       = "https://smartwallet2026.github.io"
AUTHOR         = "Alex Morgan"
ADSENSE_ID     = "ca-pub-7508482110287286"
POSTS_DIR      = "posts"
TOPICS_FILE    = "post_topics.json"

def call_gemini(prompt):
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    for attempt in range(4):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.7, max_output_tokens=3000)
            )
            return response.text.strip()
        except Exception as e:
            err = str(e)
            if "429" in err or "ResourceExhausted" in err or "RATE_LIMIT" in err:
                wait = 30 * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s (attempt {attempt+1}/4)...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini API failed after 4 retries")

def pick_topic():
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
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
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return topic

def generate_post(topic):
    prompt = f"""Write a SEO-optimized personal finance blog article.
TOPIC: {topic['title']}
KEYWORD: {topic['keyword']}
CATEGORY: {topic['category']}
Requirements: 800-1000 words, 5 H2 sections, practical advice.
OUTPUT ONLY valid JSON:
{{
  "title": "...",
  "meta_description": "...",
  "intro": "...",
  "sections": [{{"heading":"...","content":"..."}}],
  "conclusion": "...",
  "read_time": "X min read"
}}"""
    raw = call_gemini(prompt)
    raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw.strip())
    return json.loads(raw)

def build_html(topic, post):
    today = datetime.date.today()
    date_str = today.strftime("%B %d, %Y")
    date_iso = today.isoformat()
    slug = topic["slug"]
    post_url = f"{SITE_URL}/posts/{slug}.html"
    img_url = f"https://images.unsplash.com/{topic.get('image','photo-1579621970563-ebec7560ff3e')}?w=1200&q=80"
    sections_html = ""
    for sec in post.get("sections", []):
        paras = "".join(f"<p>{p.strip()}</p>" for p in sec["content"].split("\n") if p.strip())
        sections_html += f"<h2>{sec['heading']}</h2>\n{paras}\n"
    intro_html = "".join(f"<p>{p.strip()}</p>" for p in post["intro"].split("\n") if p.strip())
    concl_html = "".join(f"<p>{p.strip()}</p>" for p in post["conclusion"].split("\n") if p.strip())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
  <meta name="description" content="{post['meta_description']}">
  <meta name="robots" content="index,follow">
  <title>{post['title']} - SmartWallet</title>
  <link rel="canonical" href="{post_url}">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
  <style>
    *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--green:#0F6E56;--gl:#E1F5EE;--gm:#5DCAA5;--gd:#085041;--tx:#1a1a1a;--mu:#666;--bd:#e8e8e8;--bg:#f8f8f6;--wh:#fff}}
    body{{font-family:"DM Sans",sans-serif;background:var(--bg);color:var(--tx);line-height:1.6}}
    a{{text-decoration:none;color:inherit}}
    nav{{background:var(--wh);border-bottom:1px solid var(--bd);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100}}
    .logo{{font-family:"Playfair Display",serif;font-size:22px;font-weight:700}}.logo span{{color:var(--green)}}
    .nl{{display:flex;gap:28px;list-style:none}}.nl a{{font-size:14px;color:var(--mu)}}.nl a:hover{{color:var(--green)}}
    .at{{font-family:"Playfair Display",serif;font-size:34px;font-weight:700;line-height:1.25;margin-bottom:14px}}
    .ab{{font-size:17px;line-height:1.85}}.ab p{{margin-bottom:20px}}.ab h2{{font-family:"Playfair Display",serif;font-size:24px;color:var(--gd);margin:36px 0 14px}}
    .hi{{width:100%;max-height:400px;object-fit:cover;display:block}}
    .aw{{max-width:760px;margin:0 auto;padding:0 24px}}
    footer{{background:var(--wh);border-top:1px solid var(--bd);padding:24px 40px;display:flex;justify-content:space-between;margin-top:40px}}
    .fll{{display:flex;gap:24px;list-style:none}}.fll a{{font-size:13px;color:var(--mu)}}
  </style>
</head>
<body>
<nav><a href="/" class="logo">Smart<span>Wallet</span></a>
  <ul class="nl"><li><a href="/">Home</a></li><li><a href="/about.html">About</a></li></ul>
</nav>
<img class="hi" src="{img_url}" alt="{post['title']}">
<div class="aw">
  <h1 class="at" style="margin-top:28px">{post['title']}</h1>
  <p style="font-size:13px;color:var(--mu);margin-bottom:28px">{AUTHOR} &middot; {date_str} &middot; {post.get('read_time','7 min read')}</p>
  <article class="ab">{intro_html}{sections_html}<h2>Final Thoughts</h2>{concl_html}</article>
</div>
<footer>
  <b>SmartWallet</b>
  <ul class="fll"><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/about.html">About</a></li><li><a href="/contact.html">Contact</a></li></ul>
  <span style="font-size:12px;color:var(--mu)">&copy; 2026 SmartWallet</span>
</footer></body></html>"""

def save_post(slug, html):
    os.makedirs(POSTS_DIR, exist_ok=True)
    path = os.path.join(POSTS_DIR, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {path}")

def main():
    if not GEMINI_API_KEY:
        raise SystemExit("GEMINI_API_KEY not set")
    topic = pick_topic()
    if not topic:
        return
    print(f"Generating: {topic['title']}")
    post = generate_post(topic)
    html = build_html(topic, post)
    save_post(topic["slug"], html)
    print(f"Done! posts/{topic['slug']}.html")

if __name__ == "__main__":
    main()
