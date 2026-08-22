#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt
npm ci
npm run build
python manage.py collectstatic --noinput
python manage.py check --deploy
