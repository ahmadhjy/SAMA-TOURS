# PythonAnywhere launch checklist

Repo: **https://github.com/ahmadhjy/SAMA-TOURS**

Replace `yourusername` with your PythonAnywhere username (e.g. `ahmadhjy`).

## Before you start

- [ ] PythonAnywhere account with **Web** + **PostgreSQL** plan
- [ ] GitHub repo pushed (done from your PC)

## On PythonAnywhere

### 1. Clone

```bash
cd ~
git clone https://github.com/ahmadhjy/SAMA-TOURS.git
cd SAMA-TOURS
```

### 2. Virtualenv

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment variables (Web tab → Environment variables)

| Variable | Value |
|----------|--------|
| `SECRET_KEY` | Generate a long random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourusername.pythonanywhere.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://yourusername.pythonanywhere.com` |
| `USE_WHITENOISE` | `True` |
| `DB_NAME` | From **Databases** tab |
| `DB_USER` | Your PA username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | `yourusername.postgres.pythonanywhere-services.com` |
| `DB_PORT` | `5432` |

### 4. Database & static

```bash
source venv/bin/activate
cd ~/SAMA-TOURS
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
mkdir -p media
```

### 5. Web app settings

| Setting | Path |
|---------|------|
| Source code | `/home/yourusername/SAMA-TOURS` |
| Working directory | `/home/yourusername/SAMA-TOURS` |
| Virtualenv | `/home/yourusername/SAMA-TOURS/venv` |

**Static files:**

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/SAMA-TOURS/staticfiles` |
| `/media/` | `/home/yourusername/SAMA-TOURS/media` |

**WSGI file** — see `DEPLOYMENT.md` Step 9.

### 6. Reload

Web tab → **Reload** → visit `https://yourusername.pythonanywhere.com`

### 7. Admin

- URL: `/admin/`
- Add packages, visa PDFs, testimonials

---

Full details: [DEPLOYMENT.md](DEPLOYMENT.md)
