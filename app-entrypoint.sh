#!/usr/bin/env bash
set -e

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

echo "Migrating..."
./manage.py makemigrations
./manage.py migrate

echo "-------------------------------------"
echo "#  Creating user with:              #"
echo "#       username: admin             #"
echo "#       password: pass              #"
echo "-------------------------------------"


exec "$@"