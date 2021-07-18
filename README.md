# OCmusic
Let's talk about music ...

[![Build Status](https://travis-ci.com/titou386/OCmusic.svg?branch=main)](https://travis-ci.com/github/titou386/OCmusic)

OCMusic is a music chatting web application based on Django framework.

## Features
- Free account creation
- Read artist profile, the content of an album, song detail
- Read comments
- Post a comment (account required)
- Set your favorites (account required)
- Leave a message to OCmusic

## Installation
### Requirements :

- python3
- postgresql 
- pip3
- API credentials from spotify
```bash
$ pip install -r requirements/dev.txt
```

### Set your environment:

In .env file :
```bash
CLIENT_ID="YOUR_SPOTIFY_CLIENT_ID"
CLIENT_SECRET="YOUR_SPOTIFY_CLIENT_SECRET"
DJANGO_SETTINGS_MODULE=ocmusic.settings.devel
SECRET_KEY="YOUR_KEY" # or run the command below and paste it here.
DB_NAME="YOUR_DATABASE_NAME"
DB_USER="YOUR_DATABASE_USER"
DB_PASSWORD="USER'S_PASSWORD"
DB_HOST="DATABASE_HOSTNAME_OR_IP"
DB_PORT="5432"
```

For a random new key:
```bash
$ python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### Start the app:

```bash
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

For read messages :
```bash
$ python3 manage.py createsuperuser
```

Run the app for testing only:
```bash
$ python3 manage.py runserver
```