from django.db import models


class SpotifySession(models.Model):
    client_id = models.CharField(max_length=32, unique=True)
    access_token = models.CharField(max_length=100, blank=True)
    token_type = models.CharField(max_length=10, blank=True)
    token_expires = models.DateTimeField()
