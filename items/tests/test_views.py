from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from items.spotify import SpotifyAPI
from items.models import SpotifySession

import os
import datetime
import json


@patch.dict(os.environ, {"CLIENT_ID": "ABCDF", "CLIENT_SECRET": "12345"})
class ViewsTestCase(TestCase):
    def setUp(self):
        SpotifySession.objects.create(
            client_id="ABCDF",
            access_token="NgCXRKcMzYjw",
            token_type="bearer",
            token_expires=datetime.datetime.now() + datetime.timedelta(seconds=30))

    @patch.object(SpotifyAPI, 'requester', return_value=json.loads(open("items/tests/search.json").read()))
    def test_search_view_context(self, *args):
        response = self.client.get(reverse("search"), {'query': 'test'})
        self.assertEqual(len(response.context_data['spotify']), 3)
        self.assertEqual(response.context_data['query'], 'test')

    @patch.object(SpotifyAPI, 'requester',
                  return_value=json.loads(open("items/tests/album.json").read()))
    def test_album_view_context(self, *args):
        response = self.client.get(reverse("album-details", kwargs={'album_id': 'hjskdfhjkd'}))
        self.assertTrue(response.context_data['spotify']['name'])

    @patch.object(SpotifyAPI, 'requester',
                  return_value=json.loads(open("items/tests/search.json").read())['artists']['items'][0])
    def test_artist_view_context(self, *args):
        response = self.client.get(reverse("artist-details", kwargs={'artist_id': 'hjskdfhjkd'}))
        self.assertTrue(response.context_data['spotify']['name'])

    @patch.object(SpotifyAPI, 'requester', return_value={"artists": []})
    def test_track_view_context(self, *args):
        response = self.client.get(reverse("track-details", kwargs={'track_id': 'hjskdfhjkd'}))
        self.assertEqual(response.status_code, 200)
