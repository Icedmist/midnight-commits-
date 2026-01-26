 import requests
from bs4 import BeautifulSoup

def get_tech_news():
    print("--- 📰 Hacker News Scraper ---")
    print("Tip: Works best with 'https://news.ycombinator.com/' or its sub-pages.")
    
    # 1. Allow User Input (with a default fallback)
    default_url = "https://news.ycombinator.com/"
    url = input(f"\nEnter URL (Press Enter for '{default_url}'): ").strip()
    
    if not url:
        url = default_url

    try:
        print(f"📡 Connecting to {url}...")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ Failed to load page. Status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 2. Scrape specific Hacker News tags
        story_spans = soup.find_all('span', class_='titleline')

        if not story_spans:
            print("\n⚠️  No articles found!")
            print("Reason: The URL you entered might not be Hacker News, or their code changed.")
            print(f"DEBUG: We looked for <span class='titleline'> but found nothing.")
            return

        print(f"\n✅ Found {len(story_spans)} articles.\n")

        for index, span in enumerate(story_spans[:10], start=1):
            link_tag = span.find('a')
            if link_tag:
                title = link_tag.get_text()
                link = link_tag.get('href')
                print(f"{index}. {title}")
                print(f"   🔗 {link}\n")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    get_tech_news()