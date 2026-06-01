# Deploy Sama Tours to PythonAnywhere (with PostgreSQL)

Step-by-step guide to push the project to GitHub and deploy on PythonAnywhere.

---

## Part 1 — Push to GitHub (on your PC)

### Step 1: Initialize Git (if not done yet)

Open PowerShell in the project folder:

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
git init
git add .
git commit -m "Prepare Sama Tours for production deployment"
```

### Step 2: Create a GitHub repository

1. Go to [github.com/new](https://github.com/new)
2. Name it e.g. `sama-tours`
3. Keep it **Private** (recommended)
4. Do **not** add README or .gitignore (you already have them)
5. Click **Create repository**

### Step 3: Push your code

Replace `YOUR_USERNAME` with your GitHub username:

```powershell
git remote add origin https://github.com/ahmadhjy/SAMA-TOURS.git
git branch -M main
git push -u origin main
```

---

## Part 2 — Set up PythonAnywhere

### Step 4: Create a Web App

1. Log in to [pythonanywhere.com](https://www.pythonanywhere.com)
2. Go to **Web** → **Add a new web app**
3. Choose **Manual configuration** (not Django wizard — we already have a project)
4. Select **Python 3.10** or **3.11**

### Step 5: Clone from GitHub

Open a **Bash console** on PythonAnywhere:

```bash
cd ~
git clone https://github.com/ahmadhjy/SAMA-TOURS.git
cd SAMA-TOURS
```

### Step 6: Create virtual environment & install packages

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 7: Configure environment variables

On PythonAnywhere, go to **Web** → your app → **Environment variables** (or edit WSGI file).

Add these (use your real values):

| Variable | Example |
|----------|---------|
| `SECRET_KEY` | long random string |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourusername.pythonanywhere.com` |
| `CSRF_TRUSTED_ORIGINS` | `https://yourusername.pythonanywhere.com` |
| `USE_WHITENOISE` | `True` |
| `DB_NAME` | from Databases tab |
| `DB_USER` | your PA username |
| `DB_PASSWORD` | your PostgreSQL password |
| `DB_HOST` | `yourusername.postgres.pythonanywhere-services.com` |
| `DB_PORT` | `5432` |

**PostgreSQL credentials:** Dashboard → **Databases** → PostgreSQL → copy host, database name, user, password.

Database name format is usually: `yourusername$samatours`

### Step 8: Run migrations & create admin

In the Bash console (venv activated):

```bash
cd ~/SAMA-TOURS
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

Optional — sample content:

```bash
python manage.py seed_content
```

### Step 9: Configure the Web app

**Web** tab → **Code**:

| Setting | Value |
|---------|-------|
| **Source code** | `/home/yourusername/SAMA-TOURS` |
| **Working directory** | `/home/yourusername/SAMA-TOURS` |
| **Virtualenv** | `/home/yourusername/SAMA-TOURS/venv` |

**WSGI configuration file** — replace contents with:

```python
import os
import sys

path = '/home/yourusername/SAMA-TOURS'
if path not in sys.path:
    sys.path.insert(0, path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samatours.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Replace `yourusername` with your PythonAnywhere username.

### Step 10: Static & media files

**Static files** mapping (Web tab):

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/yourusername/SAMA-TOURS/staticfiles` |
| `/media/` | `/home/yourusername/SAMA-TOURS/media` |

Create media folder if needed:

```bash
mkdir -p ~/SAMA-TOURS/media
```

Click **Reload** on the Web tab.

---

## Part 3 — Updating the live site

When you make changes locally:

```powershell
git add .
git commit -m "Describe your change"
git push
```

On PythonAnywhere Bash console:

```bash
cd ~/SAMA-TOURS
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then **Reload** the web app.

---

## Adding packages (Admin)

1. Visit `https://yourusername.pythonanywhere.com/admin/`
2. **Travel packages** → **Add**
3. Fill in:
   - **Name** — package title
   - **Destination** — e.g. `Dubai, UAE`
   - **Duration** — e.g. `5 Days / 4 Nights`
   - **Starting price** — number only, e.g. `899` (shows as "From $899")
   - **Short description**
   - **Featured image** — upload the main photo
4. Save — **Book Now** automatically links to WhatsApp.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| 502 / import error | Check WSGI path and virtualenv path |
| Static files missing | Run `collectstatic`, check static files mapping |
| Uploads not showing | Check `/media/` mapping and folder permissions |
| CSRF error on admin | Add your HTTPS URL to `CSRF_TRUSTED_ORIGINS` |
| Database error | Verify PostgreSQL env vars in Web → Environment variables |

---

## Custom domain (optional)

If you point `samatourslb.com` to PythonAnywhere:

1. Add CNAME in your domain DNS
2. Add domain in PythonAnywhere **Web** → **Domains**
3. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` with your domain
4. Enable HTTPS (free on PA paid plans)
