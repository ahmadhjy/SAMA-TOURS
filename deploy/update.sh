#!/usr/bin/env bash
#
# Sama Tours — production update (PythonAnywhere)
#
# One-time setup:
#   cd ~/SAMA-TOURS
#   cp deploy/production.env.example deploy/production.env
#   nano deploy/production.env          # paste values from your WSGI file
#   chmod +x deploy/update.sh
#
# Every update after you push to GitHub:
#   cd ~/SAMA-TOURS && ./deploy/update.sh
#
set -euo pipefail

PROJECT_DIR="/home/Samatours2026/SAMA-TOURS"
VENV_DIR="/home/Samatours2026/.virtualenvs/sama-website"
ENV_FILE="${PROJECT_DIR}/deploy/production.env"
GIT_BRANCH="${GIT_BRANCH:-main}"

log() { printf '\n==> %s\n' "$1"; }
die() { printf '\nERROR: %s\n' "$1" >&2; exit 1; }

if [[ ! -d "$PROJECT_DIR" ]]; then
    die "Project folder not found: $PROJECT_DIR"
fi

cd "$PROJECT_DIR"

if [[ ! -f "$ENV_FILE" ]]; then
    die "Missing $ENV_FILE — run: cp deploy/production.env.example deploy/production.env && nano deploy/production.env"
fi

if [[ ! -f "$VENV_DIR/bin/activate" ]]; then
    die "Virtualenv not found: $VENV_DIR"
fi

# Server should match GitHub. Drop local edits to tracked files (e.g. old manual CSS uploads).
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
    log "Resetting local edits to tracked files (uploads in media/ are not affected)"
    git reset --hard HEAD
fi

log "Loading production environment"
set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
export DJANGO_SETTINGS_MODULE=config.settings.production

if [[ "$DJANGO_SECRET_KEY" == replace-with-your-secret-key* ]]; then
    die "Edit deploy/production.env — set DJANGO_SECRET_KEY from your WSGI file"
fi
if [[ "$DJANGO_DB_PASSWORD" == replace-with-db-password* ]]; then
    die "Edit deploy/production.env — set DJANGO_DB_PASSWORD from your WSGI file"
fi

log "Activating virtualenv: sama-website"
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

log "Pulling latest code from GitHub (branch: $GIT_BRANCH)"
git fetch origin "$GIT_BRANCH"
git pull --ff-only origin "$GIT_BRANCH"

log "Installing Python dependencies"
pip install -r requirements.txt --disable-pip-version-check -q

log "Checking database connection"
python manage.py check --database default

PENDING="$(python manage.py showmigrations --plan 2>/dev/null | grep -c '\[ \]' || true)"
if [[ "$PENDING" -gt 0 ]]; then
    log "Applying $PENDING pending migration(s) (existing data is preserved)"
    python manage.py migrate --noinput
else
    log "No pending migrations"
fi

log "Collecting static files"
python manage.py collectstatic --noinput

if [[ -n "${PA_WSGI_FILE:-}" && -f "$PA_WSGI_FILE" ]]; then
    log "Reloading web app via WSGI touch"
    touch "$PA_WSGI_FILE"
else
    log "Reload manually: Web tab → your WEBSITE app → Reload (not the ERP app)"
fi

log "Done. Site: https://${DJANGO_ALLOWED_HOSTS%%,*}/"
