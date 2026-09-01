# Sanish Backend — Deployment Guide

## Prerequisites
- GitHub account (repo must be public or Render must have access)
- Render account (render.com)
- Cloudflare account with R2 enabled
- Netlify account (frontend already deployed)

---

## 1. Cloudflare R2 Setup

1. Go to Cloudflare Dashboard → R2
2. Create a bucket named `sanish-media`
3. Under R2 → Manage R2 API Tokens → Create Token
   - Permissions: Object Read & Write
   - Bucket: `sanish-media`
4. Note:
   - **Access Key ID** → `R2_ACCESS_KEY_ID`
   - **Secret Access Key** → `R2_SECRET_ACCESS_KEY`
   - **Account ID** → used in endpoint URL
   - **Endpoint URL**: `https://<account-id>.r2.cloudflarestorage.com`

---

## 2. Deploy to Render (Blueprint)

### Option A: One-click Blueprint
1. Push this repo to GitHub
2. Go to [render.com/deploy](https://render.com) → New → Blueprint
3. Select your repo; Render reads `render.yaml` and provisions:
   - A **Web Service** (Python, `gunicorn`)
   - A **PostgreSQL** database
4. Set the **secret** environment variables (not in render.yaml, marked `sync: false`):
   | Variable | Value |
   |---|---|
   | `R2_ACCESS_KEY_ID` | from Cloudflare |
   | `R2_SECRET_ACCESS_KEY` | from Cloudflare |
   | `R2_ENDPOINT_URL` | `https://<accountid>.r2.cloudflarestorage.com` |
5. Click **Apply** — Render runs `build.sh` automatically

### Option B: Manual Service
1. New → Web Service → connect repo
2. **Build Command**: `./build.sh`
3. **Start Command**: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
4. **Environment**: Python
5. Add all env vars from `.env.example` (prod values)

---

## 3. Create First Superuser

After the first successful deploy, open the Render **Shell** tab:

```bash
python manage.py createsuperuser
```

Or use the standard Django admin at `/django-admin/` (username/password set above).

Then visit `/cms/` to access the Sanish CMS dashboard.

---

## 4. Custom Domains

### API Domain (`api.sanishlaminate.com`)
1. Render → your web service → Settings → Custom Domains
2. Add `api.sanishlaminate.com`
3. In your DNS provider, add CNAME:
   - Host: `api`
   - Value: `<your-service>.onrender.com`

### Admin Domain (`admin.sanishlaminate.com`) — optional
Same process as above but point to the same web service.

---

## 5. Connect Next.js Frontend

In your Netlify dashboard (or `.env.local` for local dev), set:

```
NEXT_PUBLIC_API_URL=https://api.sanishlaminate.com
```

The Next.js site fetches:
- `${NEXT_PUBLIC_API_URL}/api/products/` — product list (ISR)
- `${NEXT_PUBLIC_API_URL}/api/products/{slug}/` — product detail
- `${NEXT_PUBLIC_API_URL}/api/city-pages/` — generateStaticParams
- `${NEXT_PUBLIC_API_URL}/api/city-pages/{slug}/` — page content + SEO + JSON-LD
- `${NEXT_PUBLIC_API_URL}/api/blog/` — blog list
- `${NEXT_PUBLIC_API_URL}/api/dealers/?city=...` — dealer locator

Replace `src/lib/products.ts` static data with API calls using Next.js `fetch()` with `{ next: { revalidate: 3600 } }` for ISR.

---

## 6. Local Development

```bash
# Clone and set up
git clone <repo>
cd sanish-backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env
# Edit .env — leave DATABASE_URL blank for SQLite

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Load sample data
python manage.py loaddata fixtures/initial_data.json

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

Visit:
- **CMS**: http://localhost:8000/cms/
- **API**: http://localhost:8000/api/products/
- **Django Admin**: http://localhost:8000/django-admin/

---

## 7. Render Tier Notes

- **Starter Web Service**: Free tier — sleeps after 15 min inactivity (cold starts ~30s)
- **Starter PostgreSQL**: Free 90-day trial → upgrade to paid or export/reimport data before expiry
- For production: upgrade both to at least the **Basic** tier ($7/mo web + $7/mo DB)

---

## 8. CORS

The API only allows origins listed in `CORS_ALLOWED_ORIGINS`. Update this env var when:
- You add a custom domain to the Netlify site
- You add a staging environment

Example: `https://sanishlaminate.com,https://www.sanishlaminate.com,https://staging.sanishlaminate.netlify.app`

---

## 9. Media URL Pattern

All uploaded files are stored in Cloudflare R2. URLs look like:
```
https://<accountid>.r2.cloudflarestorage.com/sanish-media/media/uncategorized/image.webp
```

For public URLs, configure R2 public access or use a Cloudflare custom domain for the bucket.

---

## 10. Sitemap

Auto-generated at: `https://api.sanishlaminate.com/sitemap.xml`

Submit to Google Search Console after first deploy. Reference it in `robots.txt` (editable via CMS → SEO → Global Settings).
