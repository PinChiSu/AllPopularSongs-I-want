import argparse
import datetime
import psycopg2
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import re

# Set up PostgreSQL
DATABASE_NAME = 'song_stars'
DATABASE_USER = 'pinchi'
DATABASE_PASSWORD = 'Pinch0000'
# Check date format
DATE_LENGTH = 10


class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.client = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope="user-library-read"
        ))

    def get_playlist_tracks(self, playlist_url):
        playlist_id = re.search(r'playlist\/(.*)\?', playlist_url).group(1)
        return self.client.playlist_items(playlist_id)['items']

    def search_and_store_tracks(self, keyword):
        # Search for public playlists containing keyword and return playlists
        playlists = self.client.search(
            q=keyword,
            type='playlist',
            limit=5
        )['playlists']['items']
        tracks = []
        for playlist in playlists:
            playlist_tracks = self.client.playlist_items(
                playlist.get('id'),
                limit=30
            )['items']
            tracks += playlist_tracks
        return tracks


class Database:
    def __init__(self, host, database, user, table_name):
        self.conn = psycopg2.connect(
            host=host,
            database=database,
            user=user
        )
        self.cur = self.conn.cursor()
        self.table_name = table_name

    def create_tracks_table(self):
        self.cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255),
                artist VARCHAR(255),
                album VARCHAR(255),
                release_date DATE,
                duration INTERVAL,
                popularity INT
            )
        """)
        self.conn.commit()

    def insert_track(
        self,
        track_id,
        track_name,
        artist_name,
        album_name,
        release_date,
        duration_ms,
        popularity
    ):
        duration = datetime.timedelta(milliseconds=duration_ms)
        self.cur.execute(
            f"""
            INSERT INTO {self.table_name} (
                id,
                name,
                artist,
                album,
                release_date,
                duration,
                popularity
            )
            SELECT %s, %s, %s, %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM tracks WHERE id = %s
            )
            ON CONFLICT (id) DO NOTHING
            """,
            (
                track_id,
                track_name,
                artist_name,
                album_name,
                release_date,
                duration,
                popularity,
                track_id
            )
        )
        self.conn.commit()
        print(f"Inserted track {track_id} - {track_name}")

    def close(self):
        self.cur.close()
        self.conn.close()


class PlaylistImporter:
    def __init__(self, keyword, client, database):
        # self.playlist_url = playlist_url
        self.client = client
        self.database = database
        self.keyword = keyword

    def modify_date(self, date):
        """
        >>> modify_date('2019')
        '2019-01-01'
        >>> modify_date('2023-03-10')
        '2023-03-10'
        """
        if len(date) == DATE_LENGTH:
            return date
        # if we only have year data, set the month and day to 01-01
        if len(date) == 4:
            date += '-01-01'
            return date
        return date

    def import_playlist(self):
        tracks = self.client.search_and_store_tracks(self.keyword)
        for item in tracks:
            track = item['track']
            track_id = track['id']
            track_name = track['name']
            artist_name = track['artists'][0]['name']
            album_name = track['album']['name']
            duration_ms = track['duration_ms']
            popularity = track['popularity']
            release_date = track['album']['release_date']
            self.database.insert_track(
                track_id,
                track_name,
                artist_name,
                album_name,
                self.modify_date(release_date),
                duration_ms,
                popularity
            )


def parse_args():
    parser = argparse.ArgumentParser(description='Scrape data using Spotipy')
    parser.add_argument('--id', type=str, required=True,
                        help='Spotify API client ID')
    parser.add_argument('--s', type=str, required=True,
                        help='Spotify API secret')
    parser.add_argument('--k', type=str, help='Keyword for searching playlists')
    return parser.parse_args()


def main():
    # Create a Spotify client and a database connection
    args = parse_args()
    client_id, secret, keyword = args.id, args.s, args.k
    spotify_client = SpotifyClient(client_id, secret, 'http://localhost:3000/')
    database = Database('localhost', 'song_stars', 'pinchi', 'keyword_tracks')

    # Create the 'tracks' table if it doesn't exist yet
    database.create_tracks_table()

    # Import the playlist into the database
    playlist_importer = PlaylistImporter(
        keyword,  # get the keyword
        spotify_client,
        database
    )
    playlist_importer.import_playlist()
    # Close the database connection
    database.close()


if __name__ == '__main__':
    main()
