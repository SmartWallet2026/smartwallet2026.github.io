#!/usr/bin/env python3
import os, json, random, re, datetime, time, urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
SITE_URL       = "https://smartwallet2026.github.io"
AUTHOR         = "Alex Morgan"
ADSENSE_ID     = "ca-pub-7508482110287286"
POSTS_DIR      = "posts"
TOPICS_FILE    = "post_topics.json"

def call_gemini(prompt, retries=4):
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 3000}
    }).encode()
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 30 * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s (attempt {attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError("Gemini API failed after retries")

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
    prompt = f"""Write a comprehensive, SEO-optimized personal finance blog article.

TOPIC: {topic['title']}
KEYWORD: {topic['keyword']}
CATEGORY: {topic['category']}

Requirements:
- Title: max 60 chars, include keyword
- Meta description: 150-160 chars, include keyword
- Body: 800-1000 words, practical tips, step-by-step
- 5 sections with H2 headings
- Friendly, professional tone
- Specific numbers and examples

OUTPUT as JSON only (no markdown):
{{
  "title": "...",
  "meta_description": "...",
  "intro": "...",
  "sections": [
    {{"heading": "...", "content": "..."}}
  ],
  "conclusion": "...",
  "read_time": "X min read"
}}"""
    raw = call_gemini(prompt)
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("Could not parse JSON from Gemini response")

def build_html(topic, post):
    today = datetime.date.today()
    date_str = today.strftime("%B %d, %Y")
    date_iso = today.isoformat()
    slug = topic["slug"]
    post_url = f"{SITE_URL}/posts/{slug}.html"
    img_url = f"https://images.unsplash.com/{topic.get('image', 'photo-1579621970563-ebec7560ff3e')}?w=1200&q=80"

    sections_html = ""
    for sec in post.get("sections", []):
        paragraphs = "".join(f"<p>{p.strip()}</p>" for p in sec["content"].split("\n") if p.strip())
        sections_html += f"<h2>{sec['heading']}</h2>\n{paragraphs}\n"

    intro_html = "".join(f"<p>{p.strip()}</p>" for p in post["intro"].split("\n") if p.strip())
    concl_html = "".join(f"<p>{p.strip()}</p>" for p in post["conclusion"].split("\n") if p.strip())

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="{post['meta_description']}">
  <meta name="robots" content="index, follow">
  <meta property="og:title" content="{post['title']}">
  <meta property="og:description" content="{post['meta_description']}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{post_url}">
  <title>{post['title']} - SmartWallet</title>
  <link rel="canonical" href="{post_url}">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=DM+Sans:wght@400;500&display=swap" rel="stylesheet">
  <script type="application/ld+json">
  {{"@context":"https://schema.org","@type":"Article","headline":"{post['title']}","author":{{"@type":"Person","name":"{AUTHOR}"}},"datePublished":"{date_iso}","url":"{post_url}"}}
  </script>
  <style>
    *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
    :root{{--green:#0F6E56;--green-light:#E1F5EE;--green-mid:#5DCAA5;--green-dark:#085041;--text:#1a1a1a;--muted:#666;--border:#e8e8e8;--bg:#f8f8f6;--white:#fff}}
    body{{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);line-height:1.6}}
    a{{text-decoration:none;color:inherit}}
    nav{{background:var(--white);border-bottom:1px solid var(--border);padding:0 40px;display:flex;align-items:center;justify-content:space-between;height:64px;position:sticky;top:0;z-index:100}}
    .logo{{font-family:'Playfair Display',serif;font-size:22px;font-weight:700}}.logo span{{color:var(--green)}}
    .nav-links{{display:flex;gap:28px;list-style:none}}.nav-links a{{font-size:14px;color:var(--muted);font-weight:500}}.nav-links a:hover{{color:var(--green)}}
    .subscribe-btn{{background:var(--green);color:#fff;border:none;padding:9px 20px;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer}}
    .hero-img{{width:100%;max-height:400px;object-fit:cover;display:block}}
    .article-wrap{{max-width:760px;margin:0 auto;padding:0 24px}}
    .breadcrumb{{font-size:13px;color:var(--muted);padding:20px 0 0}}.breadcrumb a{{color:var(--green)}}
    .article-header{{padding:28px 0 24px;border-bottom:1px solid var(--border);margin-bottom:32px}}
    .article-tag{{display:inline-block;background:var(--green-light);color:var(--green);font-size:11px;font-weight:600;padding:4px 10px;border-radius:4px;text-transform:uppercase;margin-bottom:14px}}
    .article-title{{font-family:'Playfair Display',serif;font-size:34px;font-weight:700;line-height:1.25;margin-bottom:14px}}
    .article-meta{{display:flex;align-items:center;gap:12px;font-size:13px;color:var(--muted)}}
    .avatar{{width:32px;height:32px;border-radius:50%;background:var(--green-light);display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600;color:var(--green)}}
    .article-body{{font-size:17px;line-height:1.85;color:#2a2a2a}}
    .article-body p{{margin-bottom:20px}}.article-body h2{{font-family:'Playfair Display',serif;font-size:24px;color:var(--green-dark);margin:36px 0 14px}}
    .ad-slot{{margin:32px 0;text-align:center}}
    .cta-box{{background:var(--green-dark);color:#fff;border-radius:14px;padding:32px;text-align:center;margin:40px 0}}
    .cta-box h3{{font-family:'Playfair Display',serif;font-size:22px;margin-bottom:10px}}.cta-box p{{font-size:15px;color:#9FE1CB;margin-bottom:20px}}
    .cta-form{{display:flex;gap:10px;justify-content:center;max-width:400px;margin:0 auto}}
    .cta-input{{flex:1;padding:10px 14px;border-radius:8px;border:none;font-size:14px}}
    .cta-btn{{background:var(--green-mid);color:var(--green-dark);border:none;padding:10px 20px;border-radius:8px;font-size:13px;font-weight:600;cursor:pointer}}
    footer{{background:var(--white);border-top:1px solid var(--border);padding:24px 40px;display:flex;align-items:center;justify-content:space-between;margin-top:40px}}
    .footer-logo{{font-family:'Playfair Display',serif;font-size:18px;font-weight:700}}.footer-logo span{{color:var(--green)}}
    .footer-links{{display:flex;gap:24px;list-style:none}}.footer-links a{{font-size:13px;color:var(--muted)}}.footer-links a:hover{{color:var(--green)}}
    .footer-copy{{font-size:12px;color:var(--muted)}}
    @media(max-width:768px){{nav{{padding:0 16px}}.nav-links{{display:none}}.article-title{{font-size:26px}}.cta-form{{flex-direction:column}}footer{{flex-direction:column;gap:12px;text-align:center}}}}
  </style>
</head>
<body>
<nav>
  <a href="/" class="logo">Smart<span>Wallet</span></a>
  <ul class="nav-links">
    <li><a href="/">Saving Tips</a></li><li><a href="/">Budgeting</a></li>
    <li><a href="/">Investing</a></li><li><a href="/">Make Money</a></li>
    <li><a href="/about.html">About</a></li>
  </ul>
  <button class="subscribe-btn">Subscribe Free</button>
</nav>
<img class="hero-img" src="{img_url}" alt="{post['title']}">
<div class="article-wrap">
  <p class="breadcrumb"><a href="/">Home</a> › <a href="/">{topic['category']}</a></p>
  <header class="article-header">
    <span class="article-tag">{topic['category']}</span>
    <h1 class="article-title">{post['title']}</h1>
    <div class="article-meta">
      <div class="avatar">AM</div>
      <span>{AUTHOR}</span><span>·</span>
      <span>{date_str}</span><span>·</span>
      <span>{post.get('read_time','7 min read')}</span>
    </div>
  </header>
  <div class="ad-slot">
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_ID}" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>
  </div>
  <article class="article-body">
    {intro_html}
    {sections_html}
    <h2>Final Thoughts</h2>
    {concl_html}
  </article>
  <div class="cta-box">
    <h3>Get Smarter With Money</h3>
    <p>Weekly personal finance tips — free, no spam.</p>
    <div class="cta-form">
      <input class="cta-input" type="email" placeholder="Your email address">
      <button class="cta-btn">Subscribe Free</button>
    </div>
  </div>
</div>
<footer>
  <div class="footer-logo">Smart<span>Wallet</span></div>
  <ul class="footer-links">
    <li><a href="/privacy-policy.html">Privacy Policy</a></li>
    <li><a href="/about.html">About</a></li>
    <li><a href="/contact.html">Contact</a></li>
  </ul>
  <div class="footer-copy">© 2026 SmartWallet · All rights reserved</div>
</footer>
</body>
</html>"""

def save_post(slug, html):
    os.makedirs(POSTS_DIR, exist_ok=True)
    path = os.path.join(POSTS_DIR, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {path}")

def main():
    if not GEMINI_API_KEY:
        raise SystemExit("GEMINI_API_KEY not set")
    print("Picking topic...")
    topic = pick_topic()
    if not topic:
        return
    print(f"Generating: {topic['title']}")
    post = generate_post(topic)
    print("Building HTML...")
    html = build_html(topic, post)
    save_post(topic["slug"], html)
    print(f"Done! posts/{topic['slug']}.html")

if __name__ == "__main__":
    main()
