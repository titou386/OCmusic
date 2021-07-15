from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="items/index.html"), name="items"),
    path("search/", views.SearchView.as_view(), name="items-search"),
    path(
        "artist/<str:idx>",
        views.ArtistDetailsView.as_view(),
        name="artist-details",
    ),
    path(
        "album/<str:idx>",
        views.AlbumDetailsView.as_view(),
        name="album-details",
    ),
    path(
        "track/<str:idx>",
        views.TrackDetailsView.as_view(),
        name="track-details",
    ),
    path(
        "<str:item_type>/<str:idx>/comment/save/",
        views.CommentCreateView.as_view(),
        name="comment-create",
    ),
]
