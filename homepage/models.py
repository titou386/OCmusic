# from django.db import models
from django.db import models

# Create your models here.

class ContactForm(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=20)
    message = models.TextField()
    ip = models.CharField(max_length=40)
    posted_datetime = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
