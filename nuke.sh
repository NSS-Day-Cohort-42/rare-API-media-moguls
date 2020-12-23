#!/bin/bash

rm -rf rareapi/migrations
rm db.sqlite3
python manage.py makemigrations rareapi
python manage.py migrate
python manage.py loaddata users
python manage.py loaddata tokens
python manage.py loaddata rareusers
python manage.py loaddata categories
python manage.py loaddata tags
python manage.py loaddata posts
python manage.py loaddata posttags
python manage.py loaddata comments
python manage.py loaddata subscriptions
python manage.py loaddata reactions
python manage.py loaddata postreactions
python manage.py loaddata profileimages
