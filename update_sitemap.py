#!/usr/bin/env python3
"""
Sitemap Updater for SmartWallet
Scans all HTML files and regenerates sitemap.xml automatically.
"""

import os
import glob
import datetime

SITE_URL     = "https://smartwallet2026.github.io"
SITEMAP_FILE = "sitemap.xml"

# Static pages with their priorities
STATIC_PAGES = [
    {"url": "/",                    "priority": "1.0", "changefreq": "daily"},
    {"url": "/about.html",          "priority": "0.7", "changefreq": "monthly"},
    {"url": "/privacy-policy.html", "priority": "0.5", "changefreq": "monthly"},
    {"url": "/contact.html",        "priority": "0.6", "changefreq": "monthly"},
]

def get_post_files():
    """Get all HTML files from posts/ directory."""
    return sorted(glob.glob("posts/*.html"))

def generate_sitemap():
    today = datetime.date.today().isoformat()
    urls  = []

    # Add static pages
    for page in STATIC_PAGES:
        urls.append(f"""  <url>
    <loc>{SITE_URL}{page['url']}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{page['changefreq']}</changefreq>
    <priority>{page['priority']}</priority>
  </url>""")

    # Add blog posts
    post_files = get_post_files()
    for filepath in post_files:
        slug = os.path.basename(filepath)
        urls.append(f"""  <url>
    <loc>{SITE_URL}/posts/{slug}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""

    with open(SITEMAP_FILE, "w", encoding="utf-8") as f:
        f.write(sitemap)

    total = len(STATIC_PAGES) + len(post_files)
    print(f"✅ Sitemap updated: {total} URLs ({len(post_files)} posts)")

if __name__ == "__main__":
    generate_sitemap()
