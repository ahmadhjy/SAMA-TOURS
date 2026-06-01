# Sama Tours Website

Marketing website for Sama Tours Lebanon — Django templates, packages, visa PDFs, WhatsApp booking.

**Production deploy:** [DEPLOY.md](DEPLOY.md) (PythonAnywhere account `Samatours2026`, separate from ERP).

## Local development

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
.\djangoenv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Uses `config.settings.development` (SQLite) by default.

## Project layout

```
config/settings/     base, development, production
website/             models, views, admin
deploy/              PythonAnywhere WSGI example
templates/           HTML pages
static/              CSS, JS, logo (committed)
```

## Admin — add packages

`/admin/` → **Travel packages** → upload image, destination, duration, **starting price**, description. **Book Now** links to WhatsApp automatically.

## GitHub

https://github.com/ahmadhjy/SAMA-TOURS
