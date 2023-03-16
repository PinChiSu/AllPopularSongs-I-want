import psycopg2
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from get_data import (
    DATABASE_NAME,
    DATABASE_USER,
    DATABASE_PASSWORD,
    parse_args,
)


class PlaylistCreator:
    def __init__(self, client_id, secret):
        self.client_id = client_id
        self.secret = secret

    def _get_track_ids(self):
        conn = psycopg2.connect(
            database=DATABASE_NAME,
            user=DATABASE_USER,
            password=DATABASE_PASSWORD,
            host="localhost",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT id FROM get_popular_songs")
        return [result[0] for result in cur.fetchall()]

    def _authenticate_spotify(self):
        return spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=self.client_id,
                client_secret=self.secret,
                redirect_uri='http://localhost:3000/',
                scope='playlist-modify-public'
            )
        )

    def create_playlist(self):
        sp = self._authenticate_spotify()
        playlist_name = "My New Playlist From side project using keywords"
        playlist_description = "A new playlist created from dbt data"
        playlist = sp.user_playlist_create(
            sp.current_user()["id"],
            playlist_name,
            public=True,
            description=playlist_description
        )
        track_ids = self._get_track_ids()
        sp.user_playlist_add_tracks(
            sp.current_user()["id"],
            playlist["id"],
            track_ids
        )


if __name__ == '__main__':
    client_id, secret = parse_args()
    creator = PlaylistCreator(client_id, secret)
    creator.create_playlist()
