from core.playlist_crawler import PlaylistCrawler
import os


def main():
    username = os.getenv('SPOTIFY_USERNAME', None)
    playlist = os.getenv('SPOTIFY_PLAYLIST', None)
    crawler = PlaylistCrawler(username, playlist)

    print(crawler.get_playlist_json())


if __name__ == '__main__':
    main()
