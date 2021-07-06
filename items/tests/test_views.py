from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse
from items.spotify import SpotifyAPI
from items.models import SpotifySession

import os
import datetime


@patch.dict(os.environ, {"CLIENT_ID": "ABCDF", "CLIENT_SECRET": "12345"})
class ViewsTestCase(TestCase):
    def setUp(self):
        SpotifySession.objects.create(
            client_id="ABCDF",
            access_token="NgCXRKcMzYjw",
            token_type="bearer",
            token_expires=datetime.datetime.now() + datetime.timedelta(seconds=3600))

    @patch.object(SpotifyAPI, 'requester', return_value={
        "albums": {
            "items": [
                {
                    "name": "sqrgqsrgqregt",
                    "id": "kgjqmslbdbqde"
                }
            ]
        },
        "tracks": {
            "items": [
                {
                    "name": "geqwrgfgr",
                    "id": "jhdskgfjh"
                }
            ]
        }
    })
    def test_search_view_context(self, *args):
        response = self.client.get(reverse("search"), {'query': 'test'})
        self.assertEqual(len(response.context_data['spotify']), 2)
        self.assertEqual(response.context_data['query'], 'test')
