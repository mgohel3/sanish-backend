FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=config.settings.staging

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libpq-dev curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Tailwind standalone CLI — builds the CMS dashboard stylesheet (see build.sh)
ARG TAILWIND_VERSION=3.4.17
RUN curl -sL -o /usr/local/bin/tailwindcss \
        "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-x64" \
    && chmod +x /usr/local/bin/tailwindcss

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN tailwindcss -c tailwind.config.js -i static/css/input.css -o static/css/output.css --minify \
    && chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", \
     "--access-logfile", "-", "--error-logfile", "-"]
