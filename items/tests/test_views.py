from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from items.services import SpotifyAPI
from items.models import SpotifySession
from constants import SPOTIFY_AUTH
from items.views import Spotify

import os
import datetime
import json
import requests_mock


@patch.dict(os.environ, {"CLIENT_ID": "ABCDF", "CLIENT_SECRET": "12345"})
class ViewsSuccessTestCase(TestCase):
    def setUp(self):
        SpotifySession.objects.create(
            client_id="ABCDF",
            access_token="NgCXRKcMzYjw",
            token_type="bearer",
            token_expires=datetime.datetime.now() + datetime.timedelta(seconds=3600),
        )

    @patch.object(
        SpotifyAPI,
        "requester",
        return_value=json.loads(open("items/tests/search.json").read()),
    )
    def test_search_view_context(self, *args):
        response = self.client.get(reverse("items-search"), {"query": "test"})
        self.assertEqual(len(response.context_data["spotify"]), 3)
        self.assertEqual(response.context_data["query"], "test")

    @patch.object(
        SpotifyAPI,
        "requester",
        return_value=json.loads(open("items/tests/album.json").read()),
    )
    def test_album_view_context(self, *args):
        response = self.client.get(
            reverse("album-details", kwargs={"idx": "hjskdfhjkd"})
        )
        self.assertTrue(response.context_data["spotify"]["name"])

    @patch.object(
        SpotifyAPI,
        "requester",
        return_value=json.loads(open("items/tests/search.json").read())["artists"][
            "items"
        ][0],
    )
    def test_artist_view_context(self, *args):
        response = self.client.get(
            reverse("artist-details", kwargs={"idx": "hjskdfhjkd"})
        )
        self.assertTrue(response.context_data["spotify"]["name"])

    @patch.object(SpotifyAPI, "requester", return_value={"artists": []})
    def test_track_view_context(self, *args):
        response = self.client.get(
            reverse("track-details", kwargs={"idx": "hjskdfhjkd"})
        )
        self.assertEqual(response.status_code, 200)


@patch.dict(os.environ, {"CLIENT_ID": "ABCDF", "CLIENT_SECRET": "12345"})
class RenewTokenTestCase(TestCase):
    def setUp(self):
        SpotifySession.objects.create(
            client_id="ABCDF",
            access_token="NgCXRKcMzYjw",
            token_type="bearer",
            token_expires=datetime.datetime.now(),
        )

    def test_success_renew_token(self):
        with requests_mock.Mocker() as m:
            m.post(
                SPOTIFY_AUTH,
                json={
                    "access_token": "kfdgGL54dleGE4SQh",
                    "token_type": "bearer",
                    "expires_in": 3600,
                },
            )

            s = Spotify()
            self.assertEqual(s.spotify.access_token, "kfdgGL54dleGE4SQh")
