import os, json, random, re, datetime, time
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
POSTS_DIR      = "posts"
TOPICS_FILE    = "post_topics.json"

def call_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set.")
    genai.configure(api_key=GEMINI_API_KEY)
    
    models = ["gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"]
    last_err = None
    
    for model_name in models:
        try:
            print(f"Trying model: {model_name}")
            model = genai.GenerativeModel(model_name)
            # Add simple retry for rate limit inside the fallback loop
            for attempt in range(2):
                try:
                    response = model.generate_content(prompt)
                    return response.text.strip()
                except Exception as e:
                    if "429" in str(e):
                        time.sleep(10)
                        continue
                    raise e
        except Exception as e:
            print(f"Model {model_name} failed: {e}")
            last_err = e
            continue
            
    raise last_err

def main():
    if not os.path.exists(TOPICS_FILE):
        print(f"File {TOPICS_FILE} not found.")
        return

    with open(TOPICS_FILE, "r") as f:
        data = json.load(f)
        topics = data.get("topics", [])

    selected_topic = None
    for topic in topics:
        if not topic.get("published"):
            selected_topic = topic
            break
    
    if not selected_topic:
        print("No more topics to publish.")
        return

    print(f"Generating post for: {selected_topic['title']}")
    
    prompt = f"Write a SEO-friendly financial blog post in English about: \"{selected_topic['title']}\". Return only the HTML body content (without <html>, <head>, or <body> tags). Use h1, h2, p, ul, li tags and optimize for SEO keywords."
    
    html_content = call_gemini(prompt)
    if "<body>" in html_content:
        match = re.search(r"<body>(.*?)</body>", html_content, re.DOTALL)
        if match: html_content = match.group(1)
    
    if not os.path.exists(POSTS_DIR):
        os.makedirs(POSTS_DIR)
        
    slug = selected_topic['slug']
    filename = os.path.join(POSTS_DIR, f"{slug}.html")
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    selected_topic["published"] = True
    selected_topic["date"] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    with open(TOPICS_FILE, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Created: {filename}")

if __name__ == '__main__':
    main()
