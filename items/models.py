from django.db import models
from account.models import User


class SpotifySession(models.Model):
    client_id = models.CharField(max_length=32, primary_key=True)
    access_token = models.CharField(max_length=100, null=True, blank=True)
    token_type = models.CharField(max_length=10, null=True, blank=True)
    token_expires = models.DateTimeField(auto_now=True)


class Item(models.Model):
    idx = models.CharField(max_length=32, primary_key=True)
    name = models.CharField(max_length=128)
    like = models.ManyToManyField(User, related_name="liked")


class Album(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)
    small_img = models.CharField(max_length=128, null=True)
    medium_img = models.CharField(max_length=128, null=True)
    large_img = models.CharField(max_length=128, null=True)


class Artist(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)
    small_img = models.CharField(max_length=128, null=True)
    medium_img = models.CharField(max_length=128, null=True)
    large_img = models.CharField(max_length=128, null=True)
    album = models.ManyToManyField(Album, related_name="compositor")


class Track(models.Model):
    item = models.OneToOneField(Item, on_delete=models.CASCADE, primary_key=True)
    artist = models.ManyToManyField(Artist, related_name="singer")
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    text = models.TextField()
    created_datetime = models.DateTimeField(auto_now_add=True)
    published_by = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
