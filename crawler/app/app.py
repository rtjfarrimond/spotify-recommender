from core.playlist_crawler import PlaylistCrawler
import json
import wget
import os


def main():
    username = os.getenv('SPOTIFY_USERNAME', None)
    playlist = os.getenv('SPOTIFY_PLAYLIST', None)
    audio_path = os.getenv('AUDIO_PATH', './audio')
    if not os.path.exists(audio_path):
        os.mkdir(audio_path)
    crawler = PlaylistCrawler(username, playlist, audio_path)
    crawler.download_previews()


if __name__ == '__main__':
    main()
