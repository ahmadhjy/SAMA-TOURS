# Sama Tours Website

Modern travel agency website built with Django 5.

## Local development

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
.\djangoenv\Scripts\Activate.ps1
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Adding packages (Admin)

1. Go to `/admin/` → **Travel packages** → **Add**
2. **Name** — package title
3. **Destination** — e.g. `Dubai, UAE`
4. **Duration** — e.g. `5 Days / 4 Nights`
5. **Starting price** — e.g. `899` (displays as "From $899", used for filtering)
6. **Short description**
7. **Featured image** — upload the main photo
8. Save — **Book Now** opens WhatsApp automatically

## Package filters

Homepage and `/packages/` support filtering by:
- **Destination** — type or pick from suggestions
- **Max price** — dropdown ranges

## Production deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for full step-by-step guide:
- Push to GitHub
- Deploy on PythonAnywhere with PostgreSQL
- Static files, media uploads, environment variables

Copy `.env.example` to `.env` for local production testing (never commit `.env`).
