import cloudscraper
from bs4 import BeautifulSoup
import datetime
import yagmail
import os
import json
import time
import random
import re  # 用於正則處理
from dotenv import load_dotenv

# === 載入 .env 設定 ===
load_dotenv()
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")
NEWS_FILE = os.getenv("NEWS_FILE", "ai_news.json")

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "windows", "mobile": False}
)

def get_soup(url, extra_headers=None, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/114.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive"
    }
    if extra_headers:
        headers.update(extra_headers)
    try:
        response = scraper.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        time.sleep(random.uniform(1, 3))
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def fetch_summary(url, selector):
    soup = get_soup(url)
    if soup:
        tag = soup.select_one(selector)
        if tag:
            if tag.has_attr("content"):
                return tag["content"].strip()
            return tag.get_text(strip=True)
    return "(no summary)"

def truncate_summary(text, limit=400):
    return text[:limit] + "..." if len(text) > limit else text

# === 示範新聞網站 A ===
def fetch_demo_site_a():
    print("[Demo Site A] Fetching...")
    url = "https://demo-site-a.example.com/ai"
    soup = get_soup(url)
    news = []
    if soup:
        articles = soup.select("div[data-article='true']")
        for article in articles[:15]:
            a_tag = article.select_one("a.article-link")
            title_tag = article.select_one("h2.article-title")
            if not (a_tag and title_tag):
                continue
            link = a_tag.get("href", "")
            if not link.startswith("http"):
                link = "https://demo-site-a.example.com" + link
            title = title_tag.get_text(strip=True)
            summary = fetch_summary(link, selector="div.article-summary p")
            news.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": "Demo Site A"
            })
    return news

# === 示範新聞網站 B ===
def fetch_demo_site_b():
    print("[Demo Site B] Fetching...")
    url = "https://demo-site-b.example.com/news/ai"
    soup = get_soup(url)
    news = []
    if soup:
        articles = soup.select("div.news-card")
        for article in articles[:15]:
            title_tag = article.select_one("p.title a")
            if not title_tag:
                continue
            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            if not link.startswith("http"):
                link = "https://demo-site-b.example.com" + link
            summary_tag = article.select_one("div.summary p")
            summary = summary_tag.get_text(strip=True) if summary_tag else "(no summary)"
            news.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": "Demo Site B"
            })
    return news

# === 示範新聞網站 C（使用 meta 描述） ===
def fetch_demo_site_c():
    print("[Demo Site C] Fetching...")
    url = "https://demo-site-c.example.com/ai-news"
    soup = get_soup(url)
    news = []
    if soup:
        articles = soup.select("a.article-entry")
        for a_tag in articles[:15]:
            title = a_tag.get("data-title", "").strip() or a_tag.get_text(strip=True)
            link = a_tag.get("href", "")
            if not link.startswith("http"):
                link = "https://demo-site-c.example.com" + link
            summary = fetch_summary(link, selector='meta[name="description"]')
            news.append({
                "title": title,
                "link": link,
                "summary": summary,
                "source": "Demo Site C"
            })
    return news

def fetch_all_news():
    news = fetch_demo_site_a() + fetch_demo_site_b() + fetch_demo_site_c()
    for item in news:
        item["summary"] = truncate_summary(item["summary"], limit=400)
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    with open(NEWS_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today, "news": news}, f, ensure_ascii=False, indent=2)
    print(f"Fetched {len(news)} articles.")

def send_email():
    print("Sending email...")
    if not os.path.exists(NEWS_FILE):
        print("News file not found.")
        return
    with open(NEWS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    subject = f"CoreNews.AI - {data['date']}"
    style = (
        "body{font-family:'Arial',sans-serif;line-height:1.6;background-color:#f4f4f4;margin:0;padding:20px;}"
        ".container{max-width:800px;margin:auto;}"
        ".header{text-align:center;padding-bottom:10px;margin-bottom:20px;}"
        ".news-list{display:block;}"
        ".news-item{background:#fff;padding:15px;border-radius:8px;border:1px solid #eee;box-shadow:0 2px 4px rgba(0,0,0,0.1);margin-bottom:15px;}"
        ".news-source{font-size:14px;color:#888;margin-bottom:8px;}"
        ".news-title{font-size:18px;margin:0 0 8px;}"
        ".news-title a{color:#1a0dab;text-decoration:none;}"
        ".news-title a:hover{text-decoration:underline;}"
        ".news-summary{font-size:16px;color:#333;margin:0;overflow-wrap: break-word;white-space: pre-wrap;}"
    )
    html_content = (
        f"<html><head><meta charset='utf-8'><style>{style}</style></head>"
        f"<body><div class='container'>"
        f"<div class='header'><h2>Daily AI News Digest - {data['date']}</h2></div>"
        f"<div class='news-list'>"
    )
    for item in data["news"]:
        html_content += (
            f"<div class='news-item'>"
            f"<div class='news-source'>[{item['source']}]</div>"
            f"<div class='news-title'><a href='{item['link']}' target='_blank'>{item['title']}</a></div>"
            f"<div class='news-summary'>{item['summary']}</div>"
            f"</div>"
        )
    html_content += "</div></div></body></html>"
    config_path = os.path.expanduser("~/.yagmail")
    if not os.path.exists(config_path):
        try:
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump({EMAIL_USER: EMAIL_APP_PASSWORD}, f)
            print("Created yagmail config file.")
        except Exception as e:
            print(f"Failed to create config: {e}")
            return
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_APP_PASSWORD)
        yag.send(to=EMAIL_TO, subject=subject, contents=html_content)
        print("Email sent.")
        os.remove(NEWS_FILE)
        print("News file removed.")
    except Exception as e:
        print(f"Email sending failed: {e}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "crawl":
            fetch_all_news()
        elif sys.argv[1] == "email":
            send_email()
    else:
        fetch_all_news()
        send_email()