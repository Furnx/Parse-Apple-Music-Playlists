import re
import requests
from bs4 import BeautifulSoup

def parse_apple_music_link(url):

    # Standard headers to make the request look like a normal browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("\nConnecting...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Couldn't fetch the page. (Status code: {response.status_code})")
            return
            
        soup = BeautifulSoup(response.text, 'html.parser')
        

        songs = []
        
        
        track_rows = soup.find_all('div', class_=re.compile(r'songs-list-row'))
        
        if not track_rows:
            # Fallback check if Apple updated their web player structure slightly
            track_rows = soup.find_all('div', {'role': 'row'})

        for row in track_rows:
            title_element = row.find('div', class_=re.compile(r'track-title|title'))
            artist_element = row.find('div', class_=re.compile(r'artist|sub-title')) or row.find('a', class_=re.compile(r'artist'))
            
            if title_element:
                title = title_element.get_text(strip=True)
                # Clean up artist text if it has extra spacing or links
                artist = artist_element.get_text(strip=True) if artist_element else "Unknown Artist"
                songs.append(f"{title} - {artist}")

        if not songs:
            print("No songs found. Make sure the playlist is set to 'Public' so the script can see it!")
            return

        # Save the results to a clean TXT file
        output_file = "playlist.txt"
        with open(output_file, "w", encoding="utf-16") as f:
            for index, song in enumerate(songs, start=1):
                f.write(f"{index}. {song}\n")
                
        print(f"Success! Extracted {len(songs)} songs.")
        print(f"Your clean list has been saved to: {output_file}\n")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    playlist_url = input("Paste your Apple Music playlist URL here: ").strip()
    if "music.apple.com" in playlist_url:
        parse_apple_music_link(playlist_url)
    else:
        print("Invalid URL. Please make sure it is a valid music.apple.com link.")