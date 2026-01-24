import requests
import os

def download_images(url_list, save_folder):
    if not os.path.exists(save_folder):
        os.makedirs(save_folder)

    for i, url in enumerate(url_list, start=1):
        try:
            print(f"Downloading {i}/{len(url_list)}: {url}...")
            response = requests.get(url)
            
            # Check if request was successful (Status 200)
            if response.status_code == 200:
                # Extract filename from URL or make one up
                filename = f"image_{i}.jpg"
                file_path = os.path.join(save_folder, filename)
                
                # 'wb' mode = Write Binary (images are binary data, not text)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Saved to {file_path}")
            else:
                print("Failed to retrieve image.")
                
        except Exception as e:
            print(f"Error downloading {url}: {e}")

def main():
    # A few test images (Placeholder images)
    urls = [
        "https://via.placeholder.com/150",
        "https://via.placeholder.com/300",
        "https://via.placeholder.com/450"
    ]
    
    print(f"Found {len(urls)} images to download.")
    download_images(urls, "downloaded_images")

if __name__ == "__main__":
    main()