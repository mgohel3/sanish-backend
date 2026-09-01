#!/bin/sh
# One-time TLS bootstrap for staging.sanishlaminate.com.
# Creates a throwaway self-signed cert so nginx can start, brings the stack up,
# then replaces it with a real Let's Encrypt cert via the webroot challenge.
set -e

DOMAIN="staging.sanishlaminate.com"
EMAIL="${LETSENCRYPT_EMAIL:-hellomg2024@gmail.com}"
COMPOSE="docker compose"
LIVE="/etc/letsencrypt/live/${DOMAIN}"

cd "$(dirname "$0")"

if [ ! -f .env ]; then
  echo "deploy/.env is missing — copy .env.example and fill it in first." >&2
  exit 1
fi

echo "==> Building images"
$COMPOSE build

echo "==> Creating a temporary self-signed certificate"
$COMPOSE run --rm --entrypoint "/bin/sh -c '
  mkdir -p ${LIVE} &&
  openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
    -keyout ${LIVE}/privkey.pem -out ${LIVE}/fullchain.pem \
    -subj \"/CN=${DOMAIN}\"
'" certbot

echo "==> Starting nginx + apps"
$COMPOSE up -d

echo "==> Removing the throwaway self-signed cert so certbot won't balk"
$COMPOSE run --rm --entrypoint "/bin/sh -c '
  rm -rf /etc/letsencrypt/live/${DOMAIN} \
         /etc/letsencrypt/archive/${DOMAIN} \
         /etc/letsencrypt/renewal/${DOMAIN}.conf
'" certbot

echo "==> Requesting the real certificate"
$COMPOSE run --rm --entrypoint "certbot certonly --webroot -w /var/www/certbot \
  -d ${DOMAIN} --email ${EMAIL} --agree-tos --no-eff-email --non-interactive" certbot

echo "==> Reloading nginx with the real certificate"
$COMPOSE exec nginx nginx -s reload

echo "==> Done. https://${DOMAIN} should now serve a valid certificate."
