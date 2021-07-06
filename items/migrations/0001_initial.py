# Generated by Django 3.2.4 on 2021-07-06 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SpotifySession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(max_length=32, unique=True)),
                ('access_token', models.CharField(blank=True, max_length=100)),
                ('token_type', models.CharField(blank=True, max_length=10)),
                ('token_expires', models.DateTimeField()),
            ],
        ),
    ]
