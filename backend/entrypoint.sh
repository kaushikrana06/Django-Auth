#!/bin/sh
set -e

# optional: wait for DB if you later switch from sqlite to Postgres
# until nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do echo "waiting db..."; sleep 1; done

python manage.py migrate --noinput

# collect static only if you use whitenoise & have STATIC_ROOT
# python manage.py collectstatic --noinput

# start app
exec gunicorn simple_auth.wsgi:application \
  --bind 0.0.0.0:8000 --workers 3 --access-logfile -
