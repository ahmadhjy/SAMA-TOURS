# Deploy Sama Tours Website on PythonAnywhere (Samatours2026)

Deploy the **marketing website** as a **second web app** on the same account as the ERP.  
Do **not** share database, virtualenv, WSGI, or static folders with `Sama-Acc`.

| App | URL (example) | Folder | Database |
|-----|---------------|--------|----------|
| ERP | `samatours2026.pythonanywhere.com` | `/home/Samatours2026/Sama-Acc` | `sama_acc` / `sama_app` |
| **Website** | *your second web app hostname* | `/home/Samatours2026/SAMA-TOURS` | `sama_website` / `sama_web` |

**GitHub:** https://github.com/ahmadhjy/SAMA-TOURS

---

## 1. Create website database (Postgres console)

**Databases** → **Start postgres console** (same server as ERP):

```sql
CREATE DATABASE sama_website;
CREATE USER sama_web WITH PASSWORD 'your-lowercase-app-password';
ALTER ROLE sama_web SET client_encoding TO 'utf8';
ALTER ROLE sama_web SET default_transaction_isolation TO 'read committed';
ALTER ROLE sama_web SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sama_website TO sama_web;
\c sama_website
GRANT ALL ON SCHEMA public TO sama_web;
```

Shared server (same as ERP):

- **Host:** `Samatours2026-5298.postgres.pythonanywhere-services.com`
- **Port:** `15298`

---

## 2. Clone repo (Bash console)

```bash
cd ~
git clone https://github.com/ahmadhjy/SAMA-TOURS.git
cd SAMA-TOURS
```

Use a **GitHub PAT** if the repo is private (not your GitHub password).

---

## 3. Virtualenv (separate from ERP)

```bash
mkvirtualenv --python=/usr/bin/python3.10 sama-website
workon sama-website
cd ~/SAMA-TOURS
pip install -r requirements.txt
```

ERP uses `sama-accounting` — **do not** use that venv here.

---

## 4. Add a new web app

**Web** → **Add a new web app** → Manual configuration → Python **3.10**.

| Setting | Value |
|---------|--------|
| Source code | `/home/Samatours2026/SAMA-TOURS` |
| Working directory | `/home/Samatours2026/SAMA-TOURS` |
| Virtualenv | `/home/Samatours2026/.virtualenvs/sama-website` |

Copy `deploy/pythonanywhere_wsgi.py.example` into the **WSGI configuration file** and replace:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` (your **website** hostname)
- `DJANGO_DB_PASSWORD`

Enable **Force HTTPS** on the Web tab if available.

---

## 5. Static & media mappings

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/Samatours2026/SAMA-TOURS/staticfiles` |
| `/media/` | `/home/Samatours2026/SAMA-TOURS/media` |

```bash
workon sama-website
cd ~/SAMA-TOURS
mkdir -p media
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Optional sample content:

```bash
python manage.py seed_content
```

**Web** → **Reload**.

---

## 6. Verify CSS loads

Open in browser (replace hostname):

```
https://YOUR-WEBSITE-HOST.pythonanywhere.com/static/css/main.css
```

Should return **200** with CSS content. If **404**, run `collectstatic` and check the static files mapping.

---

## 7. Admin & content

- Admin: `https://YOUR-WEBSITE-HOST.pythonanywhere.com/admin/`
- Add packages (image upload, starting price, destination)
- Upload visa PDFs

---

## Local development (PC)

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
.\djangoenv\Scripts\Activate.ps1
$env:DJANGO_SETTINGS_MODULE="config.settings.development"
python manage.py runserver
```

---

## Updates after code changes

**On PC:**

```powershell
git add .
git commit -m "Your message"
git push
```

**On PythonAnywhere:**

```bash
cd ~/SAMA-TOURS
git pull
workon sama-website
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Reload** the website web app (not the ERP app).

---

## Avoid (lessons from ERP deploy)

- Pointing website `/static/` to ERP `staticfiles`
- Reusing `sama_acc` database or `sama_app` user
- Reusing `sama-accounting` virtualenv
- One WSGI file for both projects
- Skipping `collectstatic` (unstyled pages)
- `DEBUG=True` in production

---

## Custom domain (optional)

Point `www.samatourslb.com` to the **website** web app only.  
Update `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` in WSGI, then Reload.
