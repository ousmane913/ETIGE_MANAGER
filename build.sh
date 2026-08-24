#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
cd frontend
npm ci
npm run build
cd ..
python manage.py collectstatic --noinput
python manage.py check --deploy
python manage.py migrate
python manage.py setup_roles
