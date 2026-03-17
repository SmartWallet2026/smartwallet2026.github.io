#!/usr/bin/env python3
import os, json, random, re, datetime, time


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
SITE_URL       = "https://smartwallet2026.github.io"
AUTHOR         = "Alex Morgan"
ADSENSE_ID     = "ca-pub-7508482110287286"
POSTS_DIR      = "posts"
TOPICS_FILE    = "post_topics.json"


def call_gemini(prompt: str) -> str:
    import google.generativeai as genai
    import time
    
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set.")
        
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash-latest")
    
    for attempt in range(5):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(temperature=0.7, max_output_tokens=3000)
            )
            return response.text.strip()
        except Exception as e:
            if "429" in str(e):
                wait = 30 * (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise e
    raise RuntimeError("Gemini API failed after retries")

