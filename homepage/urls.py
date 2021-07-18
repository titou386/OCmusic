from django.urls import path
from . import views


urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("contact-form/", views.SaveContactFormView.as_view(), name="contact_form"),
]
