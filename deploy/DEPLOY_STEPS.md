# PythonAnywhere deployment — step by step

Website: **main-samatours2026.pythonanywhere.com**  
Project folder: **`~/SAMA-TOURS`**  
Virtualenv: **`sama-website`**

---

## A. One-time setup (do once)

### 1. Open Bash on PythonAnywhere

**Consoles** → **Bash**

### 2. Pull latest code

```bash
cd ~/SAMA-TOURS
git pull origin main
```

If `git pull` fails because of old manual edits:

```bash
git reset --hard HEAD
git pull origin main
```

### 3. Create secrets file

```bash
cp deploy/production.env.example deploy/production.env
nano deploy/production.env
```

Replace **only these two placeholders** with values from **Web tab → WSGI configuration file**:

- `DJANGO_SECRET_KEY=...`
- `DJANGO_DB_PASSWORD=...`

Save: **Ctrl+O** → Enter → **Ctrl+X**

### 4. Optional — auto-reload after deploy

In **Web tab**, click the WSGI file link and copy its path. Add to `deploy/production.env`:

```
PA_WSGI_FILE=/var/www/main_samatours2026_pythonanywhere_com_wsgi.py
```

(use your exact path)

### 5. Make script executable

```bash
chmod +x deploy/update.sh
```

---

## B. Every update (after you push from PC)

### On your PC

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
git add .
git commit -m "Your message"
git push origin main
```

### On PythonAnywhere (one command)

```bash
cd ~/SAMA-TOURS && ./deploy/update.sh
```

The script will:

1. Reset any old manual file edits on the server  
2. Pull from GitHub  
3. Install Python packages  
4. Apply pending migrations (safe — keeps your data)  
5. Run collectstatic  
6. Reload the app (if `PA_WSGI_FILE` is set)

If you did not set `PA_WSGI_FILE`, go to **Web tab → Reload** (website app only).

### Check the site

https://main-samatours2026.pythonanywhere.com/

Hard refresh: **Ctrl+Shift+R**

---

## C. Troubleshooting

| Problem | Fix |
|--------|-----|
| `Missing deploy/production.env` | Run step A.3 |
| `set DJANGO_SECRET_KEY` / password error | Edit `deploy/production.env` with real values from WSGI |
| Site has no CSS | Run `./deploy/update.sh` again, then Reload on Web tab |
| `Virtualenv not found` | Run `ls ~/.virtualenvs/` and tell us the name |
| Database error on migrate | Check DB password in `production.env` matches WSGI |

**Never delete and re-clone the repo for normal updates.**  
**Your uploaded images/PDFs in `media/` are safe** — that folder is not in git.
