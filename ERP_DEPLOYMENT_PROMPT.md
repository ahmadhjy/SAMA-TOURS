# Copy this entire prompt into Cursor for the ERP app (Sama-Acc)

---

## Context

We successfully set up **one-command deployment** for our **Sama Tours marketing website** (repo: `SAMA-TOURS`) on PythonAnywhere. I want the **same setup** for this **ERP Django app** on the same account.

### What works on SAMA-TOURS (replicate this pattern)

**Files added:**
- `deploy/update.sh` — bash script that: resets tracked local edits → loads `deploy/production.env` → activates venv → `git pull` → `pip install -r requirements.txt` → `manage.py check` → `migrate --noinput` (only if pending) → `collectstatic --noinput` → optional WSGI touch reload
- `deploy/production.env.example` — template for secrets (NOT committed)
- `deploy/DEPLOY_STEPS.md` — step-by-step guide
- `.gitignore` entry: `deploy/production.env`
- `.gitattributes`: `*.sh text eol=lf`

**Important implementation details (learned from production):**
- Do NOT use `source production.env` — bash chokes on comments/special chars. Use a `load_env_file()` function that only reads `KEY=value` lines and strips quotes/CRLF.
- Wrap `DJANGO_SECRET_KEY` and `DJANGO_DB_PASSWORD` in single quotes in the example file.
- Script should `git reset --hard HEAD` before pull if there are local edits to tracked files (server should match GitHub). `media/` uploads must NOT be affected.
- Validate that secret key and DB password are not still placeholders before deploying.
- After `git pull`, user may need `chmod +x deploy/update.sh` again.

**One-time on PythonAnywhere:**
```bash
cp deploy/production.env.example deploy/production.env
nano deploy/production.env   # values from WSGI file
chmod +x deploy/update.sh
./deploy/update.sh
# Reload ERP web app on Web tab
```

**Every update:**
```bash
cd ~/Sama-Acc && chmod +x deploy/update.sh && ./deploy/update.sh
```

---

## This app (ERP) — PythonAnywhere details

| Setting | Value |
|--------|--------|
| PA account | `Samatours2026` |
| Project folder | `/home/Samatours2026/Sama-Acc` |
| Virtualenv | `sama-accounting` → `/home/Samatours2026/.virtualenvs/sama-accounting` |
| Live URL | `samatours2026.pythonanywhere.com` |
| Database | `sama_acc` / user `sama_app` |
| Postgres host | `Samatours2026-5298.postgres.pythonanywhere-services.com` |
| Postgres port | `15298` |
| Sibling app (website) | `~/SAMA-TOURS`, venv `sama-website`, DB `sama_website` — **do not mix** |

Inspect this repo for:
- Production settings module path (e.g. `config.settings.production` or similar)
- Existing WSGI example / deploy docs
- Static files dir (`staticfiles/`)
- Media dir (`media/`)

---

## Your task

1. **Add the same `deploy/` folder** adapted for this ERP project (correct `PROJECT_DIR`, `VENV_DIR`, `DJANGO_SETTINGS_MODULE`, allowed hosts, DB names).
2. **Add `deploy/DEPLOY_STEPS.md`** with ERP-specific paths and “Reload ERP app, not website” warnings.
3. **Update `.gitignore`** for `deploy/production.env`.
4. **Add `.gitattributes`** for LF line endings on shell scripts if missing.
5. **Do not commit secrets.** `production.env.example` uses placeholders only.
6. **Push to GitHub** when done.

Do NOT re-clone or change production data. The script must be safe: migrations only apply pending ones; never flush or reset DB.

---

## Reference: working `load_env_file` + update flow

Use the same logic as SAMA-TOURS `deploy/update.sh` (commit `460c9ae` or later on https://github.com/ahmadhjy/SAMA-TOURS).

After you implement, give me:
- List of files created/changed
- Exact one-time PythonAnywhere commands for this ERP app
- Exact command for every future update
