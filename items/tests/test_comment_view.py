from django.test import TestCase
from unittest.mock import patch
from items.models import SpotifySession, User
from items.services import SpotifyAPI
from django.urls import reverse

import datetime
import json
import os


@patch.dict(os.environ, {"CLIENT_ID": "ABCDF", "CLIENT_SECRET": "12345"})
class CommentViewTestCase(TestCase):
    def setUp(self):
        SpotifySession.objects.create(
            client_id="ABCDF",
            access_token="NgCXRKcMzYjw",
            token_type="bearer",
            token_expires=datetime.datetime.now() + datetime.timedelta(seconds=3600),
        )
        u = User.objects.create(username="Michelle", email="michelle@free.fr")
        u.set_password("1234")
        u.save()

    @patch.object(
        SpotifyAPI,
        "requester",
        return_value=json.loads(open("items/tests/album.json").read()),
    )
    def test_comment_create(self, *args):
        self.client.login(username="Michelle", password="1234")
        self.client.post(
            reverse(
                "comment-create",
                kwargs={"idx": "6ZG5lRT77aJ3btmArcykra", "item_type": "album"},
            ),
            {"text": "TestTestTest"},
        )
        response = self.client.get(
            reverse("album-details", kwargs={"idx": "6ZG5lRT77aJ3btmArcykra"})
        )
        self.assertEqual(response.context_data["comments"][0].text, "TestTestTest")
