#!/usr/bin/env bash
# Local development quick-start
set -euo pipefail

echo "==> Creating virtualenv"
python -m venv .venv
source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate

echo "==> Installing dependencies"
pip install -r requirements.txt

echo "==> Copying .env"
[ -f .env ] || cp .env.example .env

echo "==> Generating migrations"
python manage.py makemigrations accounts media_library catalog pages seo blog leads

echo "==> Applying migrations"
python manage.py migrate

echo "==> Loading sample data"
python manage.py loaddata fixtures/initial_data.json

echo ""
echo "✓ Setup complete!"
echo ""
echo "  Next steps:"
echo "  1. python manage.py createsuperuser"
echo "  2. python manage.py runserver"
echo "  3. Open http://localhost:8000/cms/"
