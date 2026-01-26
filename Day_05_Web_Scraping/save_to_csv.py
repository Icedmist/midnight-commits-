import requests
from bs4 import BeautifulSoup
import csv

def scrape_and_save(filename="books_data.csv"):
    url = "http://books.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    books_data = []
    book_cards = soup.find_all('article', class_='product_pod')

    print(f"Extracting data for {len(book_cards)} books...")

    for card in book_cards:
        title = card.find('h3').find('a')['title']
        price = card.find('p', class_='price_color').get_text()
        
        # Clean the price (remove the weird Â character if it appears due to encoding)
        price = price.replace('Â', '').strip()
        
        # Star rating is a class name (e.g., "star-rating Three")
        rating_tag = card.find('p', class_='star-rating')
        # rating_tag['class'] returns a list like ['star-rating', 'Three']
        rating = rating_tag['class'][1] 

        books_data.append([title, price, rating])

    # Save to CSV
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Write Header
        writer.writerow(["Book Title", "Price", "Star Rating"])
        # Write Data
        writer.writerows(books_data)

    print(f"✅ Success! Data saved to '{filename}'.")

if __name__ == "__main__":
    scrape_and_save()