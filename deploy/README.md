# Sanish staging deploy

Single VPS (`187.127.166.131`, Hostinger KVM2, Ubuntu 24.04), Docker Compose,
one domain: **https://staging.sanishlaminate.com**.

## Stack

| Service   | Image / build            | Role |
|-----------|--------------------------|------|
| `nginx`   | nginx:1.27-alpine        | TLS termination, routing, HTTP basic auth, serves `/media/` |
| `frontend`| `../../sanish-next`      | Next.js 16 (`next start`, :3000) |
| `backend` | `..` (sanish-backend)   | Django + gunicorn (:8000), settings `config.settings.staging` |
| `db`      | postgres:16-alpine       | app database (volume `pgdata`) |
| `certbot` | certbot/certbot          | issues + auto-renews the Let's Encrypt cert |

Routing (nginx):

- `/api/`, `/static/`, `/media/`, `/sitemap.xml` → open (needed for SSR + browser)
- `/cms/`, `/django-admin/`, `/ckeditor5/`, and the whole site `/` → **HTTP basic auth**
- `/robots.txt` → hard `Disallow: /`

Media lives on a local Docker volume (`media`). Switch to Cloudflare R2 later by
setting `R2_*` and restoring the S3 storage block (see `config/settings/prod.py`).

## Server layout

```
/opt/sanish/
├── sanish-backend/          # git clone of mgohel3/sanish-backend
│   └── deploy/              # <- run docker compose from here
│       ├── .env             # secrets (NOT in git) — copy from .env.example
│       └── nginx/auth/.htpasswd   # basic-auth users (NOT in git)
└── sanish-next/             # git clone of mgohel3/sanish-next
```

## First-time bring-up

```bash
sudo mkdir -p /opt/sanish && sudo chown "$USER" /opt/sanish && cd /opt/sanish
git clone git@github.com:mgohel3/sanish-backend.git
git clone https://github.com/mgohel3/sanish-next.git

cd /opt/sanish/sanish-backend/deploy
cp .env.example .env && nano .env          # fill SECRET_KEY, POSTGRES_PASSWORD, DATABASE_URL, ...

mkdir -p nginx/auth
docker run --rm httpd:2.4-alpine htpasswd -nbB sanish 'YOUR_PASSWORD' > nginx/auth/.htpasswd

chmod +x init-letsencrypt.sh
./init-letsencrypt.sh                        # builds images, bootstraps TLS, starts everything

# seed a fresh database
docker compose exec -T backend python manage.py loaddata fixtures/initial_data.json
docker compose exec backend python manage.py createsuperuser
```

Visit https://staging.sanishlaminate.com (basic-auth prompt) and
https://staging.sanishlaminate.com/cms/ for the CMS.

## Routine ops

```bash
cd /opt/sanish/sanish-backend/deploy

docker compose ps
docker compose logs -f backend
docker compose logs -f frontend

# manual redeploy (CI does this automatically on push to master)
(cd ../ && git pull) && docker compose up -d --build backend
(cd ../../sanish-next && git pull) && docker compose up -d --build frontend

# django management
docker compose exec backend python manage.py <cmd>
```

## CI (GitHub Actions)

Both repos have `.github/workflows/deploy.yml`. On push to the default branch
(`main` for sanish-backend, `master` for sanish-next) or a manual
`workflow_dispatch`, the job SSHes in as the `deploy` user and rebuilds the
relevant service.

Repo secrets required in **each** repo:

| Secret           | Value |
|------------------|-------|
| `DEPLOY_SSH_KEY` | private key of the CI deploy key (`deploy` user is in the `docker` group) |
| `DEPLOY_HOST`    | `187.127.166.131` |
| `DEPLOY_USER`    | `deploy` |
