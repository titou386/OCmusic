import os
import datetime

from django.views.generic import TemplateView
from items.spotify import SpotifyAPI
from items.models import SpotifySession


class Spotify:
    def __init__(self):
        spotify_session, created = SpotifySession.objects.get_or_create(
            client_id=os.getenv("CLIENT_ID")
        )
        spotify_session.token_expires = spotify_session.token_expires.replace(
            tzinfo=None
        )
        if (
            created is False
            and spotify_session.token_expires is not None
            and datetime.datetime.now() < spotify_session.token_expires
        ):
            self.spotify = SpotifyAPI(
                client_id=os.getenv("CLIENT_ID"),
                client_secret=os.getenv("CLIENT_SECRET"),
                access_token=spotify_session.access_token,
                token_type=spotify_session.token_type,
                token_expires=spotify_session.token_expires,
            )
        else:
            self.spotify = SpotifyAPI(
                client_id=os.getenv("CLIENT_ID"),
                client_secret=os.getenv("CLIENT_SECRET"),
            )
            self.spotify.auth()
            SpotifySession.objects.filter(client_id=os.getenv("CLIENT_ID")).update(
                access_token=self.spotify.access_token,
                token_type=self.spotify.token_type,
                token_expires=self.spotify.token_expires,
            )


class Search(Spotify, TemplateView):
    template_name = "items/search.html"
    context_object_name = "results"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET["query"]
        context["spotify"] = self.spotify.search(self.request.GET["query"], limit=8)
        return context
