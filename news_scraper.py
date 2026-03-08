import requests
from bs4 import BeautifulSoup
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def scrape_wdwnt():
    print("Scraping WDW News Today...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Get the homepage
    url = "https://wdwnt.com"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    
    # Find article links
    articles = soup.find_all("a", href=True)
    article_urls = []
    
    for a in articles:
        href = a['href']
        if "wdwnt.com/2" in href and href not in article_urls:
            article_urls.append(href)
    
    print(f"Found {len(article_urls)} articles")
    
    comments_saved = 0
    
    # Scrape first 5 articles
    for url in article_urls[:5]:
        try:
            print(f"Scraping: {url[:60]}...")
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Get article title
            title = soup.find("h1")
            title_text = title.get_text().strip() if title else "Unknown"
            
            # Get article paragraphs
            paragraphs = soup.find_all("p")
            
            for p in paragraphs:
                text = p.get_text().strip()
                
                # Only keep substantial paragraphs
                if len(text) > 100:
                    supabase.table("raw_comments").insert({
                        "source": "wdwnt",
                        "username": "wdwnt_article",
                        "date_posted": datetime.now().isoformat(),
                        "content": text,
                        "upvotes": 0,
                        "subreddit": None,
                        "post_id": url,
                        "post_title": title_text,
                        "url": url,
                        "processed": False
                    }).execute()
                    comments_saved += 1
                    
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    print(f"\nSaved {comments_saved} paragraphs to Supabase")

scrape_wdwnt()