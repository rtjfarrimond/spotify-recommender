from core.playlist_crawler import PlaylistCrawler
import json
import wget
import os


def parse_response(response):
    for item in response['items']:
        track = item['track']
        preview_url = track['preview_url']
        if preview_url:
            spotify_id = track['id']
            name = track['name']
            artists = track['artists']
            filename = wget.download(preview_url)
            os.rename(filename, f'{name}.mp3')

def main():
    username = os.getenv('SPOTIFY_USERNAME', None)
    playlist = os.getenv('SPOTIFY_PLAYLIST', None)
    crawler = PlaylistCrawler(username, playlist)

    response = crawler.get_playlist_json()
    parse_response(response)


if __name__ == '__main__':
    main()
