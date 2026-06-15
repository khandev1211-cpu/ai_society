#!/bin/bash
echo "🛠  Dev mode — AI Society"
cd "$(dirname "$0")"
set -a && source .env && set +a
python manage.py migrate --run-syncdb
python manage.py runserver 0.0.0.0:8000
