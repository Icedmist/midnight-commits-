import requests
from bs4 import BeautifulSoup

def get_tech_news():
    url = "https://news.ycombinator.com/"
    
    try:
        print(f"📡 Connecting to {url}...")
        response = requests.get(url)
        
        # Check if the website accepted our request
        if response.status_code != 200:
            print(f"Failed to load page. Status code: {response.status_code}")
            return

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # In Hacker News, titles are in <span> tags with class 'titleline'
        # Note: Website structures change! If this breaks, inspect the site's HTML.
        story_spans = soup.find_all('span', class_='titleline')

        print(f"\nFound {len(story_spans)} articles. Here are the top 10:\n")

        for index, span in enumerate(story_spans[:10], start=1):
            # The <a> tag is inside the <span>
            link_tag = span.find('a')
            
            if link_tag:
                title = link_tag.get_text()
                link = link_tag.get('href')
                print(f"{index}. {title}")
                print(f"   🔗 {link}\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_tech_news()