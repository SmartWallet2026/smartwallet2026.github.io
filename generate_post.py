#!/usr/bin/env python3
"""
SmartWallet Auto Post Generator
Uses Google Gemini API to generate SEO-optimized blog posts
and creates HTML files ready for GitHub Pages.
"""

import os
import json
import random
import re
import datetime
import urllib.request
import urllib.parse

# ── Config ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
SITE_URL       = "https://smartwallet2026.github.io"
AUTHOR         = "Alex Morgan"
ADSENSE_ID     = "ca-pub-7508482110287286"
POSTS_DIR      = "posts"
TOPICS_FILE    = "post_topics.json"

# ── Gemini API Call ─────────────────────────────────────────────────────
def call_gemini(prompt: str) -> str:
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    )
    body = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
    }).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.loads(resp.read())
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()

# ── Pick Topic ──────────────────────────────────────────────────────────
def pick_topic() -> dict:
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    pending = [t for t in data["topics"] if not t.get("published")]
    if not pending:
        print("All topics published! Add more to post_topics.json")
        return None
    topic = random.choice(pending)
    # Mark as published
    for t in data["topics"]:
        if t["slug"] == topic["slug"]:
            t["published"] = True
            t["published_date"] = datetime.date.today().isoformat()
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return topic

# ── Generate Content ────────────────────────────────────────────────────
def generate_post(topic: dict) -> dict:
    prompt = f"""Write a comprehensive, SEO-optimized personal finance blog article with these requirements:

TOPIC: {topic['title']}
KEYWORD: {topic['keyword']}
CATEGORY: {topic['category']}

REQUIREMENTS:
1. Title: Compelling, include keyword, max 60 characters
2. Meta description: 150-160 characters, include keyword, action-oriented
3. Article body: 800-1200 words, practical advice, actionable tips
4. Structure: Introduction, 5-7 main sections with H2 headings, Conclusion
5. Tone: Friendly, professional, encouraging
6. Include: Specific numbers, examples, step-by-step tips
7. Avoid: Fluff, vague advice, filler content

OUTPUT FORMAT (JSON only, no markdown):
{{
  "title": "...",
  "meta_description": "...",
  "intro": "...",
  "sections": [
    {{"heading": "...", "content": "..."}},
    ...
  ],
  "conclusion": "...",
  "read_time": "X min read"
}}"""

    raw = call_gemini(prompt)
    # Extract JSON even if Gemini adds markdown fences
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("Could not parse JSON from Gemini response")

# ── Build HTML ──────────────────────────────────────────────────────────
def build_html(topic: dict, post: dict) -> str:
    today      = datetime.date.today()
    date_str   = today.strftime("%B %d, %Y")
    date_iso   = today.isoformat()
    slug       = topic["slug"]
    post_url   = f"{SITE_URL}/posts/{slug}.html"
    img_url    = f"https://images.unsplash.com/{topic.get('image', 'photo-1579621970563-ebec7560ff3e')}?w=1200&q=80"

    # Build article body HTML
    sections_html = ""
    for sec in post.get("sections", []):
        # Convert newlines to paragraphs
        paragraphs = "".join(
            f"<p>{p.strip()}</p>" for p in sec["content"].split("\n") if p.strip()
        )
        sections_html += f"<h2>{sec['heading']}</h2>\n{paragraphs}\n"

    intro_html   = "".join(f"<p>{p.strip()}</p>" for p in post["intro"].split("\n") if p.strip())
    concl_html   = "".join(f"<p>{p.strip()}</p>" for p in post["conclusion"].split("\n") if p.strip())

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
  <meta property="og:image" content="{img_url}">
  <meta property="article:published_time" content="{date_iso}">
  <meta property="article:author" content="{AUTHOR}">
  <title>{post['title']} — SmartWallet</title>
  <link rel="canonical" href="{post_url}">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
  <script type="application/ld+json">
  {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "{post['title']}",
    "description": "{post['meta_description']}",
    "author": {{"@type": "Person", "name": "{AUTHOR} "}},
    "publisher": {{"@type": "Organization", "name": "SmartWallet"}},
    "datePublished": "{date_iso}",
    "url": "{post_url}"
  }}
  </script>
  <style>
    *, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
    :root {{
      --green: #0F6E56; --green-light: #E1F5EE; --green-mid: #5DCAA5;
      --green-dark: #085041; --text: #1a1a1a; --text-muted: #666;
      --border: #e8e8e8; --bg: #f8f8f6; --white: #ffffff;
    }}
    body {{ font-family: 'DM Sans', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }}
    a {{ text-decoration: none; color: inherit; }}

    nav {{ background: var(--white); border-bottom: 1px solid var(--border); padding: 0 40px;
           display: flex; align-items: center; justify-content: space-between; height: 64px;
           position: sticky; top: 0; z-index: 100; }}
    .logo {{ font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 700; }}
    .logo span {{ color: var(--green); }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; }}
    .nav-links a {{ font-size: 14px; color: var(--text-muted); font-weight: 500; transition: color 0.2s; }}
    .nav-links a:hover {{ color: var(--green); }}
    .subscribe-btn {{ background: var(--green); color: #fff; border: none; padding: 9px 20px;
                      border-radius: 8px; font-size: 13px; font-weight: 500; cursor: pointer;
                      font-family: 'DM Sans', sans-serif; transition: background 0.2s; }}
    .subscribe-btn:hover {{ background: var(--green-dark); }}

    .hero-img {{ width: 100%; max-height: 420px; object-fit: cover; display: block; }}

    .article-wrap {{ max-width: 760px; margin: 0 auto; padding: 0 24px; }}
    .breadcrumb {{ font-size: 13px; color: var(--text-muted); padding: 20px 0 0; }}
    .breadcrumb a {{ color: var(--green); }}
    .article-header {{ padding: 28px 0 24px; border-bottom: 1px solid var(--border); margin-bottom: 32px; }}
    .article-tag {{ display: inline-block; background: var(--green-light); color: var(--green);
                    font-size: 11px; font-weight: 600; padding: 4px 10px; border-radius: 4px;
                    letter-spacing: 0.6px; text-transform: uppercase; margin-bottom: 14px; }}
    .article-title {{ font-family: 'Playfair Display', serif; font-size: 36px; font-weight: 700;
                      line-height: 1.25; margin-bottom: 14px; }}
    .article-meta {{ display: flex; align-items: center; gap: 12px; font-size: 13px; color: var(--text-muted); }}
    .avatar {{ width: 32px; height: 32px; border-radius: 50%; background: var(--green-light);
               display: flex; align-items: center; justify-content: center;
               font-size: 11px; font-weight: 600; color: var(--green); }}

    .article-body {{ font-size: 17px; line-height: 1.85; color: #2a2a2a; }}
    .article-body p {{ margin-bottom: 20px; }}
    .article-body h2 {{ font-family: 'Playfair Display', serif; font-size: 24px; font-weight: 700;
                        color: var(--green-dark); margin: 36px 0 14px; }}
    .article-body h3 {{ font-size: 18px; font-weight: 600; margin: 24px 0 10px; }}
    .article-body ul, .article-body ol {{ margin: 0 0 20px 24px; }}
    .article-body li {{ margin-bottom: 8px; }}
    .article-body strong {{ color: var(--text); }}

    /* AdSense slot */
    .ad-slot {{ margin: 32px 0; text-align: center; }}
    .ad-label {{ font-size: 11px; color: var(--text-muted); margin-bottom: 6px; }}

    .cta-box {{ background: var(--green-dark); color: #fff; border-radius: 14px;
                padding: 32px; text-align: center; margin: 40px 0; }}
    .cta-box h3 {{ font-family: 'Playfair Display', serif; font-size: 22px; margin-bottom: 10px; }}
    .cta-box p {{ font-size: 15px; color: #9FE1CB; margin-bottom: 20px; }}
    .cta-form {{ display: flex; gap: 10px; justify-content: center; max-width: 400px; margin: 0 auto; }}
    .cta-input {{ flex: 1; padding: 10px 14px; border-radius: 8px; border: none; font-size: 14px;
                  font-family: 'DM Sans', sans-serif; }}
    .cta-btn {{ background: var(--green-mid); color: var(--green-dark); border: none; padding: 10px 20px;
                border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; white-space: nowrap; }}

    .related {{ margin: 40px 0 56px; }}
    .related h2 {{ font-family: 'Playfair Display', serif; font-size: 20px; margin-bottom: 18px;
                   padding-bottom: 10px; border-bottom: 1px solid var(--border); }}
    .related-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .related-card {{ background: var(--white); border: 1px solid var(--border); border-radius: 10px;
                     padding: 16px; transition: box-shadow 0.2s; }}
    .related-card:hover {{ box-shadow: 0 4px 16px rgba(0,0,0,0.07); }}
    .rc-tag {{ font-size: 10px; font-weight: 600; color: var(--green); text-transform: uppercase; }}
    .rc-title {{ font-size: 13px; font-weight: 500; line-height: 1.4; margin-top: 6px; }}
    .rc-meta {{ font-size: 11px; color: var(--text-muted); margin-top: 6px; }}

    footer {{ background: var(--white); border-top: 1px solid var(--border); padding: 24px 40px;
              display: flex; align-items: center; justify-content: space-between; }}
    .footer-logo {{ font-family: 'Playfair Display', serif; font-size: 18px; font-weight: 700; }}
    .footer-logo span {{ color: var(--green); }}
    .footer-links {{ display: flex; gap: 24px; list-style: none; }}
    .footer-links a {{ font-size: 13px; color: var(--text-muted); }}
    .footer-links a:hover {{ color: var(--green); }}
    .footer-copy {{ font-size: 12px; color: var(--text-muted); }}

    @media (max-width: 768px) {{
      nav {{ padding: 0 16px; }} .nav-links {{ display: none; }}
      .article-title {{ font-size: 26px; }}
      .article-body {{ font-size: 16px; }}
      .related-grid {{ grid-template-columns: 1fr; }}
      .cta-form {{ flex-direction: column; }}
      footer {{ flex-direction: column; gap: 12px; text-align: center; }}
    }}
  </style>
</head>
<body>

<nav>
  <a href="/" class="logo">Smart<span>Wallet</span></a>
  <ul class="nav-links">
    <li><a href="/">Saving Tips</a></li>
    <li><a href="/">Budgeting</a></li>
    <li><a href="/">Investing</a></li>
    <li><a href="/">Make Money</a></li>
    <li><a href="/about.html">About</a></li>
  </ul>
  <button class="subscribe-btn">Subscribe Free</button>
</nav>

<img class="hero-img" src="{img_url}" alt="{post['title']}">

<div class="article-wrap">
  <p class="breadcrumb"><a href="/">Home</a> › <a href="/">{topic['category']}</a> › {post['title']}</p>

  <header class="article-header">
    <span class="article-tag">{topic['category']}</span>
    <h1 class="article-title">{post['title']}</h1>
    <div class="article-meta">
      <div class="avatar">AM</div>
      <span>{AUTHOR}</span>
      <span>·</span>
      <span>{date_str}</span>
      <span>·</span>
      <span>{post.get('read_time', '7 min read')}</span>
    </div>
  </header>

  <!-- AdSense Top -->
  <div class="ad-slot">
    <div class="ad-label">Advertisement</div>
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_ID}"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <article class="article-body">
    {intro_html}
    {sections_html}
    <h2>Final Thoughts</h2>
    {concl_html}
  </article>

  <!-- AdSense Mid -->
  <div class="ad-slot">
    <div class="ad-label">Advertisement</div>
    <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_ID}"
         data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
    <script>(adsbygoogle = window.adsbygoogle || []).push({{}});</script>
  </div>

  <div class="cta-box">
    <h3>Get Smarter With Money</h3>
    <p>Weekly personal finance tips — free, no spam.</p>
    <div class="cta-form">
      <input class="cta-input" type="email" placeholder="Your email address">
      <button class="cta-btn">Subscribe Free</button>
    </div>
  </div>

  <div class="related">
    <h2>More Articles You'll Love</h2>
    <div class="related-grid">
      <a href="/" class="related-card">
        <div class="rc-tag">Saving</div>
        <div class="rc-title">How to Save $1,000 in 3 Months on Any Income</div>
        <div class="rc-meta">Mar 17 · 8 min read</div>
      </a>
      <a href="/" class="related-card">
        <div class="rc-tag">Budgeting</div>
        <div class="rc-title">The 50/30/20 Rule Explained for Beginners</div>
        <div class="rc-meta">Mar 15 · 5 min read</div>
      </a>
      <a href="/" class="related-card">
        <div class="rc-tag">Investing</div>
        <div class="rc-title">How to Start Investing With Just $50 a Month</div>
        <div class="rc-meta">Mar 9 · 8 min read</div>
      </a>
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

# ── Save HTML ───────────────────────────────────────────────────────────
def save_post(slug: str, html: str):
    os.makedirs(POSTS_DIR, exist_ok=True)
    path = os.path.join(POSTS_DIR, f"{slug}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ Saved: {path}")

# ── Main ────────────────────────────────────────────────────────────────
def main():
    if not GEMINI_API_KEY:
        raise SystemExit("❌ GEMINI_API_KEY not set. Add it to GitHub Secrets.")

    print("📋 Picking topic...")
    topic = pick_topic()
    if not topic:
        return

    print(f"✍️  Generating: {topic['title']}")
    post = generate_post(topic)

    print("🔨 Building HTML...")
    html = build_html(topic, post)
    save_post(topic["slug"], html)

    print(f"🎉 Done! Post: posts/{topic['slug']}.html")
    print(f"🔗 Live URL: {SITE_URL}/posts/{topic['slug']}.html")

if __name__ == "__main__":
    main()
