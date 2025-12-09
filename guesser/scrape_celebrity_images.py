import os
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import quote
import pandas as pd

df = pd.read_csv("guesser/data/guessify_simple.csv")


celebrities=[name for name in df['name'].tolist()]
# List of all celebrities
# celebrities = [
#     "Leonardo DiCaprio", "Tom Cruise", "Johnny Depp", "Brad Pitt",
#     "Tom Hanks", "Muhammad Ali", "Ryan Reynolds", "The Weeknd",
#     "Drake", "Post Malone", "Eminem", "Ed Sheeran",
#     "Bruno Mars", "Harry Styles", "Michael Jackson", "David Bowie",
#     "Kanye West", "Taylor Swift", "Beyoncé", "Ariana Grande",
#     "Adele", "Billie Eilish", "Dua Lipa", "Rihanna",
#     "Lady Gaga", "Cristiano Ronaldo", "Lionel Messi", "Neymar Jr",
#     "LeBron James", "Kevin Durant", "Roger Federer", "Novak Djokovic",
#     "Rafael Nadal"
# ]

def download_celebrity_image_from_wikipedia(name):
    """Download celebrity image from Wikipedia"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = name.lower().replace(' ', '_').replace('é', 'e') + '.jpg'
    filepath = os.path.join(script_dir, 'static', 'images', 'celebrities', filename)
    
    # Skip if already exists
    if os.path.exists(filepath):
        print(f"⏭️  Skipped: {name} (already exists)")
        return True
    
    try:
        # Search Wikipedia
        wiki_search_url = f"https://en.wikipedia.org/wiki/{quote(name.replace(' ', '_'))}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(wiki_search_url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed: {name} - Wikipedia page not found")
            return False
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the infobox image (main celebrity photo)
        infobox = soup.find('table', {'class': 'infobox'})
        
        if infobox:
            img_tag = infobox.find('img')
            if img_tag and img_tag.get('src'):
                img_url = 'https:' + img_tag['src']
                
                # Download the image
                img_response = requests.get(img_url, headers=headers, timeout=10)
                
                if img_response.status_code == 200:
                    with open(filepath, 'wb') as f:
                        f.write(img_response.content)
                    print(f"✅ Downloaded: {name}")
                    return True
        
        print(f"⚠️  No image found: {name}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {name} - {str(e)}")
        return False

def download_all_images():
    """Download all celebrity images"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'static', 'images', 'celebrities')
    
    # Create directory if it doesn't exist
    os.makedirs(images_dir, exist_ok=True)
    
    print("=" * 80)
    print("🎬 Celebrity Image Downloader")
    print("=" * 80)
    print(f"\nDownloading {len(celebrities)} celebrity images from Wikipedia...\n")
    
    success_count = 0
    failed = []
    
    for i, celebrity in enumerate(celebrities, 1):
        print(f"[{i}/{len(celebrities)}] ", end="")
        
        if download_celebrity_image_from_wikipedia(celebrity):
            success_count += 1
        else:
            failed.append(celebrity)
        
        # Be polite to Wikipedia - add delay
        time.sleep(1)
    
    print("\n" + "=" * 80)
    print(f"✅ Successfully downloaded: {success_count}/{len(celebrities)}")
    
    if failed:
        print(f"\n⚠️  Failed to download ({len(failed)}):")
        for name in failed:
            print(f"   - {name}")
    
    print("=" * 80)

if __name__ == '__main__':
    # Install required packages
    print("Installing required packages...")
    os.system('pip install requests beautifulsoup4 -q')
    print()
    download_all_images()