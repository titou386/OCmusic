from django.test import TestCase
from items.spotify import SpotifyAPI
from constants import SPOTIFY_API

import datetime
import json
import requests_mock


class SpotifyAPITestCase(TestCase):
    def setUp(self):
        self.s = SpotifyAPI(
            "ABCDF",
            "12345",
            access_token="NgCXRKcMzYjw",
            token_type="bearer",
            token_expires=datetime.datetime.now() + datetime.timedelta(seconds=3600)
        )

    def test_related_artists(self):
        with requests_mock.Mocker() as m:
            m.get(f"{SPOTIFY_API}/artists/test/related-artists",
                  json={"artists": json.loads(open("items/tests/search.json").read())['artists']['items']})

            r = self.s.get_related_artists("test")
            self.assertEqual(len(r), 5)
