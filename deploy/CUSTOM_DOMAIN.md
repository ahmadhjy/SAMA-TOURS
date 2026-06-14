# Custom domain — samatourslb.com on PythonAnywhere

Website app: **SAMA-TOURS** (not the ERP app).

---

## What Django needs (already in `config/settings/production.py`)

Production reads hosts from **environment variables** set in the WSGI file — you do **not** edit `settings.py` on the server for this.

Required in WSGI (comma-separated, one logical string):

```python
os.environ["DJANGO_ALLOWED_HOSTS"] = (
    "main-samatours2026.pythonanywhere.com,"
    "www.samatourslb.com,"
    "samatourslb.com"
)
os.environ["DJANGO_CSRF_TRUSTED_ORIGINS"] = (
    "https://main-samatours2026.pythonanywhere.com,"
    "https://www.samatourslb.com,"
    "https://samatourslb.com"
)
```

Also update **`deploy/production.env`** on the server (for `./deploy/update.sh`) with the same `DJANGO_ALLOWED_HOSTS` and `DJANGO_CSRF_TRUSTED_ORIGINS` lines.

---

## Step 1 — PythonAnywhere: add the domain

1. Log in → **Web** tab → open your **website** app (`main-samatours2026`).
2. Scroll to **Domains**.
3. Add:
   - `www.samatourslb.com`
   - `samatourslb.com` (if your PA plan supports naked/root domain)
4. PythonAnywhere shows the exact DNS records it expects — match those in IONOS.

Your CNAME is correct for **www**:

| Type  | Host | Value                              |
|-------|------|------------------------------------|
| CNAME | www  | webapp-3087375.pythonanywhere.com  |

---

## Step 2 — Root domain `@` (samatourslb.com without www)

Right now `@ → 92.204.218.253` points to IONOS, **not** your site.

**Easiest (recommended):** In IONOS, set **domain redirect**:

- `samatourslb.com` → `https://www.samatourslb.com`

**Or** if PythonAnywhere shows an **A record** IP for the naked domain, replace `@` with that IP (paid PA accounts).

Until `@` is fixed, use **https://www.samatourslb.com** as your public URL.

---

## Step 3 — WSGI file (you did this)

Save the WSGI file, then **Reload** the web app.

Quick test in a Bash console:

```bash
cd ~/SAMA-TOURS
source ~/.virtualenvs/sama-website/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.production
export DJANGO_SECRET_KEY='...'
export DJANGO_ALLOWED_HOSTS='main-samatours2026.pythonanywhere.com,www.samatourslb.com,samatourslb.com'
python manage.py check
```

Should print: `System check identified no issues`.

---

## Step 4 — Enable HTTPS on PythonAnywhere

1. **Web** tab → your website app.
2. Find **HTTPS/SSL** (or **Security**).
3. Enable **HTTPS** / **Force HTTPS** for:
   - `www.samatourslb.com`
   - `samatourslb.com` (when configured)
4. Wait for the certificate (often a few minutes after DNS propagates).
5. **Reload** the web app again.

Django production settings already use:

- `SECURE_PROXY_SSL_HEADER`
- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`

So once PA terminates HTTPS, cookies and forms work over `https://`.

---

## Step 5 — Update `deploy/production.env`

```bash
nano ~/SAMA-TOURS/deploy/production.env
```

Set:

```
DJANGO_ALLOWED_HOSTS=main-samatours2026.pythonanywhere.com,www.samatourslb.com,samatourslb.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://main-samatours2026.pythonanywhere.com,https://www.samatourslb.com,https://samatourslb.com
```

---

## Step 6 — DNS propagation & verify

DNS can take **15 minutes to 48 hours**. Check:

```bash
nslookup www.samatourslb.com
```

Should point to PythonAnywhere (via CNAME to `webapp-3087375.pythonanywhere.com`).

Open in browser:

- https://www.samatourslb.com/
- https://main-samatours2026.pythonanywhere.com/ (should still work)

---

## Troubleshooting

| Problem | Fix |
|--------|-----|
| `DisallowedHost` error | WSGI `DJANGO_ALLOWED_HOSTS` missing that hostname; Reload web app |
| CSRF error on forms | Add `https://www.samatourslb.com` to `DJANGO_CSRF_TRUSTED_ORIGINS` |
| `www` works, bare domain doesn’t | Fix `@` redirect or A record in IONOS |
| Certificate pending | Wait for DNS; confirm CNAME in IONOS matches PA exactly |
| Old site still shows | Clear browser cache / try incognito |

---

## Security reminder

Never commit WSGI secrets or post them in chat. If credentials were shared, rotate **DJANGO_SECRET_KEY** and the database password in Postgres + WSGI + `production.env`.
