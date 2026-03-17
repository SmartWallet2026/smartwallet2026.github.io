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
    model = genai.GenerativeModel("gemini-1.5-flash")
    
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

def pick_topic():
    if not os.path.exists(TOPICS_FILE):
        return None
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    pending = [t for t in data["topics"] if not t.get("published")]
    if not pending:
        return None
    topic = random.choice(pending)
    topic["id"] = data["topics"].index(topic)
    return topic

def mark_topic_published(topic_id):
    with open(TOPICS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["topics"][topic_id]["published"] = True
    data["topics"][topic_id]["publish_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(TOPICS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text

def generate_post():
    topic = pick_topic()
    if not topic:
        print("No pending topics found.")
        return

    print(f"Generating post for topic: {topic['title']}")
    
    prompt = f"Viết một bài blog tài chính chuẩn SEO bằng tiếng Việt về chủ đề: \"{topic['title']}\"."
    html_content = call_gemini(prompt)
    
    slug = slugify(topic['title'])
    filename = f"{datetime.datetime.now().strftime('%Y-%m-%d')}-{slug}.html"
    filepath = os.path.join(POSTS_DIR, filename)

    os.makedirs(POSTS_DIR, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    mark_topic_published(topic['id'])
    print(f"Successfully generated: {filepath}")

if __name__ == "__main__":
    generate_post()
