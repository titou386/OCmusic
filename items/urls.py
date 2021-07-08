from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="items/index.html"), name="items"),
    path("search/", views.SearchView.as_view(), name="search"),
    path(
        "artist/<str:artist_id>",
        views.ArtistDetailsView.as_view(),
        name="artist-details",
    ),
    path(
        "album/<str:album_id>",
        views.AlbumDetailsView.as_view(),
        name="album-details",
    ),
    path(
        "track/<str:track_id>",
        TemplateView.as_view(template_name="items/index.html"),
        name="track-details",
    ),
]
