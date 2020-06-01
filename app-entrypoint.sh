#!/usr/bin/env bash
set -e

echo "Migrating..."
./manage.py makemigrations
./manage.py migrate

exec "$@"