from django.test import TestCase
from unittest.mock import patch
from items.models import SpotifySession, User
from items.services import SpotifyAPI
from django.urls import reverse

import json
import os
import datetime


@patch.dict(os.environ, {"CLIENT_ID": "ABCDF", "CLIENT_SECRET": "12345"})
class FavoritesViewTestCase(TestCase):
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
    def test_redirect_from_visitor_making_a_favorite(self, *args):
        response = self.client.post(
            reverse(
                "favorite-save",
                kwargs={"pk": "6ZG5lRT77aJ3btmArcykra", "item_type": "album"},
            )
        )
        self.assertEqual(response.status_code, 302)
        self

    @patch.object(
        SpotifyAPI,
        "requester",
        return_value=json.loads(open("items/tests/album.json").read()),
    )
    def test_save_delete_and_display_favorites(self, *args):
        self.client.login(username="Michelle", password="1234")

        response = self.client.get(reverse("account"))
        self.assertEqual(len(response.context_data["favorites"]), 0)

        response = self.client.get(
            reverse("album-details", kwargs={"idx": "6ZG5lRT77aJ3btmArcykra"})
        )
        self.assertFalse(response.context_data["liked"])

        self.client.post(
            reverse(
                "favorite-save",
                kwargs={"pk": "6ZG5lRT77aJ3btmArcykra", "item_type": "album"},
            )
        )

        response = self.client.get(
            reverse("album-details", kwargs={"idx": "6ZG5lRT77aJ3btmArcykra"})
        )
        self.assertTrue(response.context_data["liked"])

        response = self.client.get(reverse("account"))
        self.assertEqual(len(response.context_data["favorites"]), 1)

        self.client.post(
            reverse(
                "favorite-delete",
                kwargs={"pk": "6ZG5lRT77aJ3btmArcykra", "item_type": "album"},
            )
        )

        response = self.client.get(reverse("account"))
        self.assertEqual(len(response.context_data["favorites"]), 0)

        response = self.client.get(
            reverse("album-details", kwargs={"idx": "6ZG5lRT77aJ3btmArcykra"})
        )
        self.assertFalse(response.context_data["liked"])
