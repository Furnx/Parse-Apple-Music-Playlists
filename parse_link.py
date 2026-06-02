import re
import json
import requests
from bs4 import BeautifulSoup

def parse_apple_music_link(url):

    # Standard headers to make the request look like a normal browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (kjhtml, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print("\nConnecting...")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Couldn't fetch the page. (Status code: {response.status_code})")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        

        songs = []

        # 1. Try Apple's Internal Catalog API Endpoint
        playlist_id_match = re.search(r'/(pl\.[a-zA-Z0-9._-]+)(?:/|$)', url)

        if playlist_id_match:

            playlist_id = playlist_id_match.group(1)
            api_url = f"https://amp-api.music.apple.com/v1/catalog/us/playlists/{playlist_id}"

            try:

                api_response = requests.get(api_url, headers=headers)

                if api_response.status_code == 200:

                    data = api_response.json()
                    tracks_data = data.get('data', [{}])[0].get('relationships', {}).get('tracks', {}).get('data', [])

                    for track in tracks_data:

                        attributes = track.get('attributes', {})
                        name = attributes.get('name')
                        artist = attributes.get('artistName')

                        if name and artist:

                            songs.append(f"{name} - {artist}")

            except Exception as json_err:
                pass

        if not songs:

            script_tag = soup.find('script', type='application/ld+json')

            if script_tag:

                try:

                    data = json.loads(script_tag.string)

                    if 'track' in data:

                        for track in data['track']:

                            name = track.get('name')
                            artist = track.get('byArtist', {}).get('name', 'Unknown Artist')

                            if name:

                                songs.append(f"{name} - {artist}")

                except Exception:

                    pass

        if not songs:

            script_tags = soup.find_all('script')
            for script_tag in script_tags:
                if script_tag.string:
                    content = script_tag.string
                    if 'artistName' in content and 'name' in content:
                        try:
                            matches = re.findall(r'"name":"([^"]+)".*?"artistName":"([^"]+)"', content)
                            for name, artist in matches:
                                if name and artist and name != "Preview":
                                    songs.append(f"{name} - {artist}")
                        except:
                            pass
                        if songs:
                            break

        if not songs:

            song_meta_tags = soup.find_all('meta', attrs={"property": "music:song"})

            if not song_meta_tags:

                song_meta_tags = soup.find_all('meta', attrs={"name": "apple:title"})

            for tag in song_meta_tags:

                content_url = tag.get('content', '')

                if content_url and "music.apple.com" in content_url:

                    url_parts = content_url.split('/')

                    if len(url_parts) > 0:

                        track_slug = url_parts[-1].replace('-', ' ').title()

                        songs.append(track_slug)

        # If all fails
        if not songs:
            
            print("No songs found via API or scraping methods.")
            return

        # Save the results to a TXT file
        output_file = "playlist.txt"
        with open(output_file, "w", encoding="utf-16") as f:
            for index, song in enumerate(songs, start=1):
                f.write(f"{index}. {song}\n")
                
        print(f"Success! Extracted {len(songs)} songs.")
        print(f"Your clean list has been saved to: {output_file}\n")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    playlist_url = input("Paste URL here: ").strip()
    if "music.apple.com" in playlist_url:
        parse_apple_music_link(playlist_url)
    else:
        print("Invalid URL. Please make sure it is a valid music.apple.com link.")