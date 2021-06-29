"""Spotify.py."""
import datetime
import requests
import base64

from constants import SPOTIFY_AUTH, SPOTIFY_API
from urllib.parse import urlencode


class SpotifyAPI:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_type = None
        self.token_expires = datetime.datetime.now()

    def auth(self):
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
        if self.token_expires < datetime.datetime.now():
            if not self.auth():
                raise Exception("Authorization failed.")
        return {"Authorization": f"{self.token_type} {self.access_token}"}

    def search(self, query, search_type="album, track, artist", limit=5, offset=0):
        endpoint = "/search"
        payload = {"q": query, "type": search_type, "limit": limit, "offset": offset}
        print(f"{SPOTIFY_API}{endpoint}")
        r = self.requester(f"{SPOTIFY_API}{endpoint}", payload)
        data = {}
        if "albums" in r:
            data.update({"albums": self.albums_parser(r["albums"]["items"])})
        if "tracks" in r:
            data.update({"tracks": self.tracks_parser(r["tracks"]["items"])})
        if "artists" in r:
            data.update({"artists": self.artists_parser(r["artists"]["items"])})
        return data

    def get_artists(self, *ids):
        endpoint = "artists"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids)})
        return self.artists_parser(r["artists"])

    def get_tracks(self, *ids):
        endpoint = "tracks"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids)})
        return self.tracks_parser(r["tracks"])

    def get_albums(self, *ids):
        endpoint = "albums"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids)})
        return self.albums_parser(r["albums"])

    def artists_parser(self, data):
        artist_lst = []
        for artist in data:
            artist_dict = {}
            artist_dict.update({artist["id"]: artist["name"]})
            artist_dict.update({"images": self.images_parser(artist["images"])})
            artist_lst.append(artist_dict)
        return artist_lst

    def albums_parser(self, data):
        album_lst = []
        for album in data:
            album_dict = {}

            names = []
            for artist in album["artists"]:
                names.append({artist["id"]: artist["name"]})
            album_dict.update({"artists_names": names})

            album_dict.update({"name": album["name"]})
            album_dict.update({"id": album["id"]})
            album_dict.update({"images": self.images_parser(album["images"])})
            album_lst.append(album_dict)
        return album_lst

    def tracks_parser(self, data):
        track_lst = []
        for track in data:
            track_dict = {}

            names = []
            for artist in track["album"]["artists"]:
                names.append({artist["id"]: artist["name"]})
            track_dict.update({"artists_names": names})
            track_dict.update({"images": self.images_parser(track["album"]["images"])})

            track_dict.update({"name": track["name"]})
            track_dict.update({"id": track["id"]})
            track_lst.append(track_dict)
        return track_lst

    def images_parser(self, img_lst):
        lower_limit = 200
        upper_limit = 450
        img_dict = {}
        try:
            for img in img_lst:
                if img["height"] < lower_limit:
                    img_dict.update({"small": img["url"]})
                elif img["height"] > lower_limit and img["height"] < upper_limit:
                    img_dict.update({"medium": img["url"]})
                elif img["height"] > upper_limit:
                    img_dict.update({"large": img["url"]})
            return img_dict
        except (KeyError):
            return None

    def requester(self, url, payload):
        print(f"{url}?" + urlencode(payload))
        r = requests.get(f"{url}?" + urlencode(payload), headers=self.get_auth_header())
        print(r.text)
        if not r.ok:
            return False
        return r.json()
