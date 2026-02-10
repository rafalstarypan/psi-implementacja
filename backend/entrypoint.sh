#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "${RUN_SEEDS:-false}" = "true" ]; then
  python manage.py seed_oauth_app
  python manage.py seed_users
  python manage.py seed_animals
  python manage.py seed_behavioral_tags
  python manage.py seed_supplies
  python manage.py seed_tasks
fi

exec "$@"
