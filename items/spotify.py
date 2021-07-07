"""Spotify.py."""
import datetime
import requests
import base64
import logging

from constants import SPOTIFY_AUTH, SPOTIFY_API
from urllib.parse import urlencode


class SpotifyAPI:
    """Constructor."""
    def __init__(

        self,
        client_id,
        client_secret,
        access_token=None,
        token_type=None,
        token_expires=datetime.datetime.now(),
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.token_type = token_type
        self.token_expires = token_expires

    def auth(self):
        """Request a token to use the API."""
        client_creds = f"{self.client_id}:{self.client_secret}"
        token_data = {"grant_type": "client_credentials"}
        token_headers = {
            "Authorization": f"Basic {base64.b64encode(client_creds.encode()).decode()}"
        }
        now = datetime.datetime.now()
        r = requests.post(SPOTIFY_AUTH, data=token_data, headers=token_headers)
        if not r.ok:
            return False
        data = r.json()
        self.access_token = data["access_token"]
        self.token_type = data["token_type"]
        self.token_expires = now + datetime.timedelta(seconds=data["expires_in"])
        return True

    def get_auth_header(self):
        """Check the token validity and format the header."""
        if self.token_expires < datetime.datetime.now():
            if not self.auth():
                raise Exception("Authorization failed.")
        return {"Authorization": f"{self.token_type} {self.access_token}"}

    def search(self, query, search_type="album,track,artist", market='FR', limit=5, offset=0):
        """Searching any albums, tracks, artist from a string."""
        endpoint = "/search"
        payload = {"q": query, "type": search_type, "market": market, "limit": limit, "offset": offset}
        r = self.requester(f"{SPOTIFY_API}{endpoint}", payload)
        data = {}
        if "albums" in r:
            data["albums"] = self.albums_parser(r["albums"]["items"])
        if "tracks" in r:
            data["tracks"] = self.tracks_parser(r["tracks"]["items"])
        if "artists" in r:
            data["artists"] = self.artists_parser(r["artists"]["items"])
        return data

    def get_artists(self, *ids):
        """Get multiple artists from ids."""
        endpoint = "artists"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids)})
        return self.artists_parser(r["artists"])

    def get_artist(self, ident):
        """Get an artist from an id."""
        endpoint = "artists/"
        
    def get_tracks(self, *ids, market='FR'):
        """Get multiple tracks from ids."""
        endpoint = "tracks"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids), "market": market})
        return self.tracks_parser(r["tracks"])

    def get_track(self, ident, market='FR'):
        """Get a track from an id."""
        pass

    def get_albums(self, *ids, market='FR'):
        """Get multiple albums from ids."""
        endpoint = "albums"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids), "market": market})
        return self.album_parser(r["albums"])

    def get_album(self, ident, market='FR'):
        """Get an album form an id."""
        endpoint = "/albums/"
        r = self.requester(f"{SPOTIFY_API}{endpoint}{ident}")
        return self.album_parser(r)

    def artists_parser(self, data):
        artists = []
        for artist in data:
            artists.append(self.artist_parser(artist))
        return artists

    def artist_parser(self, artist):
        artist_data = {}
        for tag in "id", "name":
            if tag in artist:
                artist_data[tag] = artist[tag]
        if "images" in artist:
            artist_data["images"] = self.images_parser(artist["images"])
        return artist_data


    def albums_parser(self, data):
        albums = []
        for album in data:
            albums.append(self.album_parser(album))
        return albums

    def album_parser(self, album):
        album_data = {}
        names = []
        duration_total = 0

        for tag in ("name", "id", "release_date", "total_tracks"):
            if tag in album:
                album_data[tag] = album[tag]

        if "artists" in album:
            for artist in album["artists"]:
                if "id" in artist and "name" in artist:
                    names.append({"id": artist["id"], "name": artist["name"]})
                album_data["artists"] = names

        if "tracks" in album and "items" in album["tracks"]:
            album_data["tracks"] = self.tracks_parser(album["tracks"]["items"])
            for track in album_data["tracks"]:
                try:
                    duration_total += int(track["duration_ms"])
                    album_data["duration_min"] = duration_total // 60000
                except(ValueError, KeyError):
                    pass

        if "images" in album:
            album_data["images"] = self.images_parser(album["images"])
        return album_data

    def tracks_parser(self, data):
        tracks = []
        for track in data:
            tracks.append(self.track_parser(track))
        return tracks

    def track_parser(self, track):
        track_dict = {}
        names = []
        for tag in ("name", "id", "duration_ms", "track_number"):
            if tag in track:
                track_dict[tag] = track[tag]
            try:
                track_dict["duration_str"] = f'{int(track["duration_ms"]) // 60000}:{(int(track["duration_ms"]) % 60000 // 1000):02}'
            except(ValueError, KeyError):
                pass

        if "artists" in track:
            for artist in track["artists"]:
                names.append({"id": artist["id"], "name": artist["name"]})
            track_dict["artists"] = names

        if "album" in track and "images" in track["album"]:
            track_dict["images"] = self.images_parser(track["album"]["images"])
        return track_dict

    def images_parser(self, img_lst):
        lower_limit = 200
        upper_limit = 450
        img_dict = {}
        try:
            for img in img_lst:
                if img["height"] < lower_limit:
                    img_dict["small"] = img["url"]
                elif img["height"] > lower_limit and img["height"] < upper_limit:
                    img_dict["medium"] = img["url"]
                elif img["height"] > upper_limit:
                    img_dict["large"] = img["url"]
            return img_dict
        except KeyError:
            return None

    def requester(self, url, payload=None):
        try:
            if payload:
                r = requests.get(
                    f"{url}?" + urlencode(payload), headers=self.get_auth_header()
                )
            else:
                r = requests.get(url, headers=self.get_auth_header())
            if not r.ok:
                logging.error(url)
                logging.error(r.json())
                return {"error": f"{r.status_code} - {r.json()['error']['message']}"}
        except ConnectionError as e:
            logging.error(e)
            return {"error": "no connection"}

        return r.json()
