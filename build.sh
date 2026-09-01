#!/usr/bin/env bash
set -euo pipefail

echo "==> Installing Python dependencies"
pip install -r requirements.txt

echo "==> Downloading Tailwind CSS standalone CLI"
TAILWIND_VERSION="3.4.17"
curl -sLO "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-x64"
chmod +x tailwindcss-linux-x64

echo "==> Building Tailwind CSS"
./tailwindcss-linux-x64 \
  --config tailwind.config.js \
  --input  static/css/input.css \
  --output static/css/output.css \
  --minify

echo "==> Generating Django migrations"
python manage.py makemigrations --noinput

echo "==> Collecting static files"
python manage.py collectstatic --noinput

echo "==> Running database migrations"
python manage.py migrate --noinput

echo "==> Build complete!"
