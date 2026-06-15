#!/bin/bash
echo "🚀 Starting AI Society..."
cd "$(dirname "$0")"

# Load env
set -a && source .env && set +a

# Run migrations
python manage.py migrate --run-syncdb

# Collect static files
python manage.py collectstatic --noinput

# Seed models from all providers
python manage.py shell -c "
from models_registry.views import sync_models
count = sync_models()
print(f'Synced {count} models')
"

# Start server
echo "✅ Starting Daphne on 0.0.0.0:8000"
daphne -b 0.0.0.0 -p 8000 ai_society.asgi:application
