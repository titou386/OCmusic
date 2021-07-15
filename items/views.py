import os
import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, CreateView
from django.urls import reverse_lazy
from items.models import SpotifySession, Comment, Item
from items.services import ItemStorage, SpotifyAPI


class Spotify:
    def __init__(self):
        spotify_session, created = SpotifySession.objects.get_or_create(
            client_id=os.getenv("CLIENT_ID")
        )
        if not created:
            spotify_session.token_expires = spotify_session.token_expires.replace(
                tzinfo=None
            )
            spotify_session.token_expires += datetime.timedelta(hours=2)

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


class CommentsView(ListView):
    model = Comment
    context_object_name = "comments"

    def get_queryset(self):
        return super().get_queryset().filter(item=self.kwargs["idx"])


class SearchView(Spotify, TemplateView):
    template_name = "items/search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET["query"]
        context["spotify"] = self.spotify.search(self.request.GET["query"], limit=8)
        return context


class AlbumDetailsView(Spotify, CommentsView):
    template_name = "items/album_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spotify"] = self.spotify.get_album(self.kwargs["idx"])
        context["item_type"] = "album"
        return context


class ArtistDetailsView(Spotify, CommentsView):
    template_name = "items/artist_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spotify"] = self.spotify.get_artist(self.kwargs["idx"])
        if "error" not in context["spotify"]:
            context["spotify"]["top_tracks"] = self.spotify.get_top_tracks(
                self.kwargs["idx"]
            )
            context["spotify"]["discography"] = self.spotify.get_discography(
                self.kwargs["idx"], limit=6
            )
            context["spotify"]["related"] = self.spotify.get_related_artists(
                self.kwargs["idx"], limit=6
            )
        context["item_type"] = "artist"
        return context


class TrackDetailsView(Spotify, CommentsView):
    template_name = "items/track_details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["spotify"] = self.spotify.get_track(self.kwargs["idx"])
        if "artists" in context["spotify"]:
            context["spotify"]["artists"] = self.spotify.get_artists(
                [artist["id"] for artist in context["spotify"]["artists"]]
            )
        context["item_type"] = "track"
        return context


class CommentCreateView(LoginRequiredMixin, Spotify, CreateView):
    model = Comment
    fields = ["text"]

    def setup(self, request, *args, **kwargs):
        ItemStorage().create(self.spotify, kwargs["item_type"], kwargs["idx"])
        return super().setup(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.published_by = self.request.user
        form.instance.item = Item.objects.get(idx=self.kwargs["idx"])
        return super().form_valid(form)

    def get_success_url(self):
        if self.kwargs["item_type"] == "artist":
            return (
                reverse_lazy("artist-details", kwargs={"idx": self.kwargs["idx"]})
                + "#comment-form"
            )
        elif self.kwargs["item_type"] == "album":
            return (
                reverse_lazy("album-details", kwargs={"idx": self.kwargs["idx"]})
                + "#comment-form"
            )
        elif self.kwargs["item_type"] == "track":
            return (
                reverse_lazy("track-details", kwargs={"idx": self.kwargs["idx"]})
                + "#comment-form"
            )
        else:
            return reverse_lazy("index")
