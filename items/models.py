from django.db import models
from account.models import User


class SpotifySession(models.Model):
    client_id = models.CharField(max_length=32, primary_key=True)
    access_token = models.CharField(max_length=100, blank=True)
    token_type = models.CharField(max_length=10, blank=True)
    token_expires = models.DateTimeField()


class Item(models.Model):
    idx = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=64)
    like = models.ManyToManyField(User, related_name="liked")


class Artist(models.Model):
    small_img = models.CharField(max_length=128, null=True)
    medium_img = models.CharField(max_length=128, null=True)
    large_img = models.CharField(max_length=128, null=True)
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)


class Album(models.Model):
    small_img = models.CharField(max_length=128, null=True)
    medium_img = models.CharField(max_length=128, null=True)
    large_img = models.CharField(max_length=128, null=True)
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)


class Track(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    created_datetime = models.DateTimeField(auto_now_add=True)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
