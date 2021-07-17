import datetime
import requests
import base64
import logging

from constants import SPOTIFY_AUTH, SPOTIFY_API
from urllib.parse import urlencode

from items.models import Item, Album, Artist, Track


class ItemStorage:
    def get_or_create_item(self, idx, name):
        return Item.objects.get_or_create(idx=idx, defaults={"name": name})[0]

    def update_or_create_artist(self, artist):
        if "images" in artist:
            return Artist.objects.update_or_create(
                item=self.get_or_create_item(artist["id"], artist["name"]),
                defaults={
                    "small_img": artist["images"]["small"],
                    "medium_img": artist["images"]["medium"],
                    "large_img": artist["images"]["large"],
                },
            )[0]
        else:
            return Artist.objects.update_or_create(
                item=self.get_or_create_item(artist["id"], artist["name"])
            )[0]

    def update_or_create_artists(self, artists):
        return [self.update_or_create_artist(artist) for artist in artists]

    def update_or_create_track(self, track):
        track_obj = Track.objects.update_or_create(
            item=self.get_or_create_item(track["id"], track["name"])
        )[0]
        if "artists" in track:
            track_obj.artist.set(self.update_or_create_artists(track["artists"]))
        if "album" in track:
            self.update_or_create_album(track["album"]).track_set.add(track_obj)
        return track_obj

    def update_or_create_tracks(self, tracks):
        return [self.update_or_create_track(track) for track in tracks]

    def update_or_create_album(self, album):
        album_obj = Album.objects.update_or_create(
            item=self.get_or_create_item(album["id"], album["name"]),
            defaults={
                "small_img": album["images"]["small"],
                "medium_img": album["images"]["medium"],
                "large_img": album["images"]["large"],
            },
        )[0]
        if "artists" in album:
            [
                artist_obj.album.add(album_obj)
                for artist_obj in self.update_or_create_artists(album["artists"])
            ]
        if "tracks" in album:
            [
                album_obj.track_set.add(track_obj)
                for track_obj in self.update_or_create_tracks(album["tracks"])
            ]
        return album_obj

    def create(self, spotify, item_type, idx):
        try:
            Item.objects.get(idx=idx)
            return
        except Item.DoesNotExist:
            try:
                if item_type == "track":
                    return self.update_or_create_track(spotify.get_track(idx))
                if item_type == "album":
                    return self.update_or_create_album(spotify.get_album(idx))
                if item_type == "artist":
                    return self.update_or_create_artist(spotify.get_artist(idx))
            except KeyError:
                return


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

    def search(
        self, query, search_type="album,track,artist", market="FR", limit=5, offset=0
    ):
        """Searching any albums, tracks, artist from a string."""
        endpoint = "/search"
        payload = {
            "q": query,
            "type": search_type,
            "market": market,
            "limit": limit,
            "offset": offset,
        }
        r = self.requester(f"{SPOTIFY_API}{endpoint}", payload)
        data = {}
        if "albums" in r:
            data["albums"] = self.albums_parser(r["albums"]["items"])
        if "tracks" in r:
            data["tracks"] = self.tracks_parser(r["tracks"]["items"])
        if "artists" in r:
            data["artists"] = self.artists_parser(r["artists"]["items"])
        return data

    def get_artists(self, ids):
        """Get multiple artists from ids list."""
        endpoint = "/artists"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"ids": ",".join(ids)})
        if "artists" in r and "error" not in r:
            return self.artists_parser(r["artists"])
        return [r]

    def get_artist(self, idx):
        """Get an artist from an id."""
        endpoint = f"/artists/{idx}/"
        r = self.requester(f"{SPOTIFY_API}{endpoint}")
        if "error" in r:
            return r
        return self.album_parser(r)

    def get_top_tracks(self, idx, market="FR", limit=5):
        """Get an Artist's Top Tracks."""
        endpoint = f"/artists/{idx}/top-tracks"
        r = self.requester(f"{SPOTIFY_API}{endpoint}", {"market": market})
        if "tracks" in r and "error" not in r:
            return self.tracks_parser(r["tracks"])[:limit]
        return [r]

    def get_discography(self, idx, include_groups="album", market="FR", limit=5):
        """Get Spotify catalog information about an artist’s albums."""
        endpoint = f"/artists/{idx}/albums"
        r = self.requester(
            f"{SPOTIFY_API}{endpoint}",
            {"include_groups": include_groups, "market": market, "limit": limit},
        )
        if "items" in r and "error" not in r:
            return self.albums_parser(r["items"])
        return [r]

    def get_related_artists(self, idx, limit=5):
        """Get an Artist's Related Artists."""
        endpoint = f"/artists/{idx}/related-artists"
        r = self.requester(f"{SPOTIFY_API}{endpoint}")
        if "artists" in r and "error" not in r:
            return self.artists_parser(r["artists"])[:limit]
        return [r]

    def get_track(self, idx, market="FR"):
        """Get a track from an id."""
        endpoint = f"/tracks/{idx}"
        r = self.requester(f"{SPOTIFY_API}{endpoint}")
        if "error" in r:
            return r
        return self.track_parser(r)

    def get_album(self, idx, market="FR"):
        """Get an album form an id."""
        endpoint = f"/albums/{idx}"
        r = self.requester(f"{SPOTIFY_API}{endpoint}")
        if "error" in r:
            return r
        return self.album_parser(r)

    def artists_parser(self, data):
        return [self.artist_parser(artist) for artist in data]

    def artist_parser(self, artist):
        """Extracts data from searched tags."""
        artist_data = {}
        for tag in "id", "name":
            if tag in artist:
                artist_data[tag] = artist[tag]
        if "images" in artist:
            artist_data["images"] = self.images_parser(artist["images"])
        return artist_data

    def albums_parser(self, data):
        """Extract tag data from a album list."""
        return [self.album_parser(album) for album in data]

    def album_parser(self, album):
        """Extract tag data from an album."""
        album_data = {}
        duration_total = 0

        for tag in "name", "id", "release_date", "total_tracks":
            if tag in album:
                album_data[tag] = album[tag]

        if "artists" in album:
            album_data["artists"] = self.artists_parser(album["artists"])

        if "tracks" in album and "items" in album["tracks"]:
            album_data["tracks"] = self.tracks_parser(album["tracks"]["items"])
            for track in album_data["tracks"]:
                try:
                    duration_total += int(track["duration_ms"])
                    album_data["duration_min"] = duration_total // 60000
                except (ValueError, KeyError):
                    pass

        if "images" in album:
            album_data["images"] = self.images_parser(album["images"])
        return album_data

    def tracks_parser(self, data):
        """Extract tag data from a track list."""
        return [self.track_parser(track) for track in data]

    def track_parser(self, track):
        """Extract tag data from a track."""
        track_dict = {}
        for tag in "name", "id", "duration_ms", "track_number":
            if tag in track:
                track_dict[tag] = track[tag]
        try:
            track_dict[
                "duration_str"
            ] = f'{int(track["duration_ms"]) // 60000}:{(int(track["duration_ms"]) % 60000 // 1000):02}'
        except (ValueError, KeyError, TypeError):
            pass

        if "artists" in track:
            track_dict["artists"] = self.artists_parser(track["artists"])
        if "album" in track:
            track_dict["album"] = self.album_parser(track["album"])

        return track_dict

    def images_parser(self, img_lst):
        lower_limit = 200
        upper_limit = 450
        img_dict = {"large": "", "medium": "", "small": ""}
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
            return {"large": "", "medium": "", "small": ""}

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
