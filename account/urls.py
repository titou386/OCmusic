from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="account"),
    path("sign-in/", views.SignInView.as_view(), name="sign-in"),
    path("sign-up/", views.SignUpView.as_view(), name="sign-up"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
