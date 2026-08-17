# Content guide — Packages & visas (EN / AR / FR)

How to add and update **travel packages** and **visa requirements** in the Sama Tours admin, with all three languages.

---

## Before you start

| Item | Details |
|------|---------|
| **Admin URL** | [https://www.samatourslb.com/admin/](https://www.samatourslb.com/admin/) |
| **Login** | Use your Django superuser account |
| **Languages** | English (EN), Arabic (AR), French (FR) |
| **No redeploy needed** | Content saved in admin appears on the live site immediately (images/PDFs are stored on the server) |

---

## How the 3 languages work

The admin uses **Jazzmin** (a clearer layout) plus **language tabs** at the top of each form:

```
[ English ] [ العربية ] [ Français ]
```

- Fill in **English first** — it is the default language and the fallback if Arabic or French is empty.
- Switch tabs to add **Arabic** and **French** for the same record.
- One package = **one row** in the database with three versions of the text fields.
- **Images and PDFs are shared** — you upload them once; they appear on all language versions of the site.

If Arabic or French is left blank, visitors on `/ar/` or `/fr/` will see the **English text** for that field.

---

## Travel packages

### Where to go

**Admin → Website → Travel packages → Add travel package**  
(or open an existing package to edit)

### Fields that need translation (fill on all 3 tabs)

| Field | Where it appears | Tips |
|-------|------------------|------|
| **Name** | Package card & detail page title | e.g. EN: `Dubai Summer Package` · AR: `باقة صيف دبي` · FR: `Forfait été Dubaï` |
| **Duration** | Card & detail page | e.g. EN: `5 Days / 4 Nights` · AR: `5 أيام / 4 ليالٍ` · FR: `5 jours / 4 nuits` |
| **Short description** | Package card (homepage & packages list) | 1–2 sentences |
| **Full description** | Package detail page | Longer marketing copy (optional but recommended) |
| **Highlights** | Detail page bullet list | **One highlight per line** |
| **Itinerary** | Detail page day-by-day | **One day per line**, e.g. `Day 1: Arrival and hotel check-in` |
| **Included** | Green check list under itinerary | **One item per line** |
| **Excluded** | Red X list under itinerary | **One item per line** |

### Fields shared across languages (English tab only)

These are the same for EN, AR, and FR — fill them once:

| Field | Notes |
|-------|--------|
| **Slug** | Auto-generated from the English name if left blank (e.g. `dubai-summer-package`). Used in the URL. |
| **Country** | Dropdown — stored in English (e.g. `United Arab Emirates`) |
| **City** | Free text (e.g. `Dubai`) — shown as `Dubai, United Arab Emirates` |
| **Starting price** | Number only in USD (e.g. `899`) — displays as “From $899” / “ابتداءً من $899” |
| **Available from / Available to** | Date pickers — shown under package details on the public page. Leave blank if always available. |
| **Featured image** | Main photo on cards and the first gallery image |
| **Featured image URL** | Alternative if you are not uploading a file |
| **Is featured** | Show on homepage |
| **Is active** | Must be checked for the package to appear on the site |
| **Display order** | Lower numbers appear first |

### Gallery images (optional)

Scroll to **Package images** at the bottom of the package form:

- Upload extra photos or paste **External image URL** — these appear as thumbnails next to the main image
- Set **Display order** (0, 1, 2…)
- **Caption** is not translated — use English or leave blank
- The featured image is always the first gallery photo; extra rows are additional photos

### Step-by-step: add a new package

1. **Admin → Travel packages → Add**
2. **English tab**
   - Name, country, city, duration, starting price, short description
   - Full description, highlights, itinerary, included, excluded (if ready)
   - Set **Available from** and **Available to** (date pickers)
   - Upload **Featured image** and extra **Package images**
   - Check **Is active** (and **Is featured** if needed)
   - Set **Display order**
3. **العربية tab** — translate name, duration, short/full description, highlights, itinerary, included, excluded
4. **Français tab** — same fields in French
5. **Save**
6. Verify on the site:
   - `/en/packages/your-slug/`
   - `/ar/packages/your-slug/`
   - `/fr/packages/your-slug/`

### Example (all 3 languages)

**English**

- Name: `Paris City Break`
- Duration: `4 Days / 3 Nights`
- Short description: `Discover the City of Light with guided tours, museums, and charming cafés.`

**Arabic**

- Name: `عطلة قصيرة في باريس`
- Duration: `4 أيام / 3 ليالٍ`
- Short description: `اكتشف مدينة النور من خلال الجولات، المتاحف، والمقاهي الباريسية الساحرة.`

**French**

- Name: `City break à Paris`
- Duration: `4 jours / 3 nuits`
- Short description: `Découvrez la Ville Lumière avec visites guidées, musées et cafés charmants.`

---

## Visa requirements

### Where to go

**Admin → Website → Visa requirements → Add visa requirement**

### Fields that need translation

| Field | Where it appears |
|-------|------------------|
| **Country name** | Visa card title on `/en/visa/`, `/ar/visa/`, `/fr/visa/` |

Example:

- EN: `France`
- AR: `فرنسا`
- FR: `France`

### Fields shared across languages (upload once)

| Field | Notes |
|-------|--------|
| **Featured image** | Photo on the visa card |
| **Featured image URL** | Use instead of upload if needed |
| **PDF file** | **Required** for the card to work — visitors click the card to open this PDF |
| **Display order** | Sort order on the visa page |
| **Is active** | Must be checked to show on the site |

> **Important:** There is **one PDF per visa entry**. The same file opens for EN, AR, and FR. Use a PDF that works for your audience (e.g. English, bilingual, or Arabic). If you need separate PDFs per language, create **separate visa entries** with different country labels (e.g. “France (EN)” / “France (AR)”) — or ask your developer to add multi-language PDF support.

### Step-by-step: add a new visa

1. **Admin → Visa requirements → Add**
2. **English tab** — enter country name (e.g. `Turkey`)
3. **العربية tab** — e.g. `تركيا`
4. **Français tab** — e.g. `Turquie`
5. Upload **Featured image** (flag, landmark, or document preview)
6. Upload **PDF file** (visa checklist / requirements document)
7. Set **Display order** and check **Is active**
8. **Save**
9. Verify: `/en/visa/`, `/ar/visa/`, `/fr/visa/` — click the card to confirm the PDF opens

Visa cards **only appear** when a PDF file is uploaded.

---

## Quick checklist before publishing

### Packages

- [ ] English name, duration, and short description filled
- [ ] Arabic and French tabs completed (or intentionally left to fall back to English)
- [ ] Country and city set
- [ ] Starting price entered (USD number)
- [ ] Featured image uploaded
- [ ] **Is active** checked
- [ ] Slug looks correct (or auto-generated)
- [ ] Tested on `/en/`, `/ar/`, and `/fr/`

### Visas

- [ ] Country name in EN, AR, and FR
- [ ] Card image uploaded
- [ ] **PDF file** uploaded
- [ ] **Is active** checked
- [ ] PDF opens when clicking the card

---

## Tips

1. **Write English first**, then translate — keeps slug and structure consistent.
2. **Keep duration format consistent** across languages (same number of days/nights).
3. **Highlights & itinerary:** one item per line; empty lines are ignored.
4. **Price:** use numbers only (`899`, not `$899`).
5. **Hide without deleting:** uncheck **Is active** to remove from the site while keeping the record.
6. **Reorder lists:** lower **Display order** = appears first.
7. **WhatsApp booking** on packages is automatic — no extra setup per language.

---

## Troubleshooting

| Problem | What to do |
|---------|------------|
| Package not on website | Check **Is active** is enabled |
| Visa card missing | Upload a **PDF file** — cards without PDF are hidden |
| Arabic shows English text | Open the **العربية** tab and fill the translated fields |
| Image/PDF not loading | Re-upload the file; on production, ensure `/media/` is configured (already set on PythonAnywhere) |
| Wrong URL / slug | Edit **Slug** on the English tab (use lowercase and hyphens only) |
| Cannot log in to admin | Reset password via server: `python manage.py changepassword your_username` |

---

## Site URLs (for testing)

| Page | English | Arabic | French |
|------|---------|--------|--------|
| Packages list | `/en/packages/` | `/ar/packages/` | `/fr/packages/` |
| Package detail | `/en/packages/slug/` | `/ar/packages/slug/` | `/fr/packages/slug/` |
| Visa page | `/en/visa/` | `/ar/visa/` | `/fr/visa/` |

---

## Need a superuser account?

On PythonAnywhere (Bash console):

```bash
cd ~/SAMA-TOURS
source ~/.virtualenvs/sama-website/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.production
# load production.env vars if needed, or use deploy/update.sh environment
python manage.py createsuperuser
```

For local development:

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
.\djangoenv\Scripts\Activate.ps1
python manage.py createsuperuser
```
