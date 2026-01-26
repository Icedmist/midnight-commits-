import requests
from bs4 import BeautifulSoup
import time

def scrape_books():
    # This acts as a safe sandbox for scraping
    url = "http://books.toscrape.com/"
    
    print(f"📚 Fetching books from {url}...\n")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all articles with class 'product_pod' (each book card)
    books = soup.find_all('article', class_='product_pod')

    for book in books:
        # 1. Get Title (It's in the <h3> -> <a> tag)
        title_tag = book.find('h3').find('a')
        title = title_tag['title'] # We get the full title from the attribute, not just text
        
        # 2. Get Price (It's in a <p> with class 'price_color')
        price_tag = book.find('p', class_='price_color')
        price = price_tag.get_text()

        # 3. Get Availability (It's in a <p> with class 'instock availability')
        stock_tag = book.find('p', class_='instock availability')
        stock = stock_tag.get_text().strip()

        print(f"📖 {title}")
        print(f"   💰 {price} | 📦 {stock}")
        print("-" * 40)
        
        # Good Manner: Don't spam the server. Sleep a tiny bit (not strictly needed here but good habit)
        # time.sleep(0.1) 

if __name__ == "__main__":
    scrape_books()