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
        if spotify_session.token_expires:
            spotify_session.token_expires = spotify_session.token_expires.replace(
                tzinfo=None
            )
        if not created and datetime.datetime.now() < spotify_session.token_expires:
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


class SearchView(Spotify, TemplateView):
    template_name = "items/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET["query"]
        context["spotify"] = self.spotify.search(self.request.GET["query"], limit=8)
        return context


class AlbumDetailsView(Spotify, TemplateView):
    template_name = "items/album_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spotify"] = self.spotify.get_album(self.kwargs["album_id"])

        return context


class ArtistDetailsView(Spotify, TemplateView):
    template_name = "items/artist_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spotify"] = self.spotify.get_artist(self.kwargs["artist_id"])
        if "error" not in context["spotify"]:
            context["spotify"]["top_tracks"] = self.spotify.get_top_tracks(self.kwargs["artist_id"])
            context["spotify"]["discography"] = self.spotify.get_discography(self.kwargs["artist_id"], limit=6)
            context["spotify"]["related"] = self.spotify.get_related_artists(self.kwargs["artist_id"], limit=6)
        return context


class TrackDetailsView(Spotify, TemplateView):
    template_name = "items/track_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spotify"] = self.spotify.get_track(self.kwargs["track_id"])
        if "artists" in context["spotify"]:
            context["spotify"]["artists"] = self.spotify.get_artists(
                [artist["id"] for artist in context["spotify"]["artists"]])
        return context
