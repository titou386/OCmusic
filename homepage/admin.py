from django.contrib import admin
from .models import ContactForm


@admin.register(ContactForm)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['read', 'posted_datetime', 'name', 'email', 'message']
    ordering = ['read', '-posted_datetime']
