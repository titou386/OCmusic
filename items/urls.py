from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="items/index.html"), name="items"),
    path("search/", views.Search.as_view(), name="search"),
    path(
        "artist/",
        TemplateView.as_view(template_name="items/index.html"),
        name="artist-detail",
    ),
    path(
        "album/",
        TemplateView.as_view(template_name="items/index.html"),
        name="album-detail",
    ),
    path(
        "track/",
        TemplateView.as_view(template_name="items/index.html"),
        name="track-detail",
    ),
]
