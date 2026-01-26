import requests
from bs4 import BeautifulSoup

def scrape_books():
    print("--- 📚 Book Store Scraper ---")
    print("Target: 'books.toscrape.com' pages.")
    
    # 1. Allow User Input
    default_url = "http://books.toscrape.com/"
    url = input(f"\nEnter URL (Press Enter for '{default_url}'): ").strip()
    
    if not url:
        url = default_url
    
    try:
        print(f"📡 Fetching books from {url}...\n")
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"❌ Connection failed: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Scrape specific Book Store tags
        books = soup.find_all('article', class_='product_pod')

        if not books:
            print("⚠️  No books found on this page.")
            print("Check if the URL is correct or if the page is empty.")
            return

        for book in books:
            title_tag = book.find('h3').find('a')
            title = title_tag['title'] 
            
            price_tag = book.find('p', class_='price_color')
            price = price_tag.get_text()

            stock_tag = book.find('p', class_='instock availability')
            stock = stock_tag.get_text().strip()

            print(f"📖 {title}")
            print(f"   💰 {price} | 📦 {stock}")
            print("-" * 40)

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    scrape_books()