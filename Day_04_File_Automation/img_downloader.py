import yt_dlp
import os

def download_video(url, save_path):
    # Ensure save directory exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # Configuration for yt-dlp
    ydl_opts = {
        # Save file as: "Folder/VideoTitle.extension"
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'format': 'best',           # Attempt to get the best quality available
        'noplaylist': True,         # If URL is a playlist, only download the single video
        'quiet': False,             # Show progress bar
    }

    try:
        print(f"\n🔍 Scraping data from: {url}...")
        
        # Initialize the downloader
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 1. Extract Metadata (The "Scraping" part)
            info = ydl.extract_info(url, download=False)
            
            title = info.get('title', 'Unknown')
            views = info.get('view_count', 'Unknown')
            duration = info.get('duration', 0)
            
            print(f"✅ Found Video: '{title}'")
            print(f"📊 Views: {views} | ⏳ Duration: {duration}s")
            
            # 2. Download
            confirm = input("Confirm download? (y/n): ").lower()
            if confirm == 'y':
                print("⬇️  Downloading...")
                ydl.download([url])
                print("🎉 Download Complete!")
            else:
                print("Download cancelled.")

    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("--- 📺 Universal Video Downloader ---")
    print("Supports: YouTube, TikTok, X (Twitter), Vimeo, and more.")
    
    while True:
        url = input("\nEnter video URL (or 'q' to quit): ").strip()
        
        if url.lower() == 'q':
            print("Exiting...")
            break
            
        if url:
            # Save to a specific "downloads" folder to keep repo clean
            download_video(url, "downloads")
        else:
            print("Please enter a valid URL.")

if __name__ == "__main__":
    main()