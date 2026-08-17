# Swan IMS v5 — Travel insurance integration

Sama Tours travel insurance via **Swan / Cygnet IMS v5** (SIA plans in sandbox).

## API

| Item | Value |
|------|--------|
| Sandbox API base | `https://staging.cygnet-ims.com/` |
| Login | `POST /api/v5/login` |
| Get plans | `POST /api/v5/travel/plans` |
| Create contract | `POST /api/v5/travel/contract` |
| Policy PDF | `GET /api/v5/travel/contract/pdf?code=…` |
| Email policy | `POST /api/v5/travel/contract/email` |
| Postman collection | `docs/ims-v5-api.postman_collection.json` |

Auth headers on all calls after login:

- `Authorization: Bearer {access_token}`
- `Tenant: {tenant_id}` (from `user.access[0].id`)

Agency ID comes from login (`user.access[0].agency`) and is sent in plan/contract bodies.

## Environment variables

Add to `.env` / `deploy/production.env` (never commit real production passwords):

```env
SWAN_IMS_API_BASE_URL=https://staging.cygnet-ims.com/
SWAN_IMS_USERNAME=lb_api_test
SWAN_IMS_PASSWORD='lb_api_test@2026'
SWAN_IMS_SANDBOX=True
SWAN_IMS_ALLOW_CHECKOUT=True
SWAN_IMS_DEFAULT_RESIDENCE=LBN
```

| Variable | Purpose |
|----------|---------|
| `SWAN_IMS_SANDBOX` | Shows sandbox banner on site |
| `SWAN_IMS_ALLOW_CHECKOUT` | `False` on production until payment gateway is live |
| `SWAN_IMS_DEFAULT_RESIDENCE` | Default country of residence (ISO3), usually `LBN` |

## Website routes

| URL | Purpose |
|-----|---------|
| `/en/travel-insurance/` | Quote form + plan results |
| `/en/travel-insurance/purchase/` | Issue policy (POST) |
| `/en/travel-insurance/order/<id>/` | Success + PDF download |
| `/en/travel-insurance/lookup/` | Find policy by email + reference |

Homepage includes a quick quote strip → full form on travel-insurance page.

## SIA product catalog vs quoted plans

SIA’s **Going** product line (as shown in the agency portal) includes variants such as:

- Going Basic (no COVID)
- Going Basic Cov / Going Basic Cov plus sport
- Going Advanced / Going Advanced Cov / Going Advanced Plus Sport
- Going Premium

The **`POST /api/v5/travel/plans`** endpoint returns only plans that are **priced for the specific trip** (residence, destination, dates, travellers) and **enabled for your agency**. Sandbox test credentials often return a **subset** (e.g. three plans for LBN→ITA) — not the full catalog.

The website shows **all plans the API returns**; advanced filters (tier, COVID, sport, currency, price) narrow that list client-side. If a product from the SIA portal is missing, it is usually because Swan has not enabled it for API quoting on that route — contact SIA/Swan to enable the full Going range for production.

## Payment gateway (not yet)

Both **eSIM** and **travel insurance** stay in **local/sandbox** until a payment gateway is connected.

- Set `SWAN_IMS_ALLOW_CHECKOUT=False` on production until payments work.
- Set Monty eSIM live purchases behind the same gateway when ready.

## Local testing

```powershell
cd "C:\Users\ME\Desktop\Sama Tours"
.\djangoenv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Visit: http://localhost:8000/en/travel-insurance/

Sandbox issues test policies in the IMS test environment (SIA plans).

## Code map

- `website/swan_ims.py` — API client
- `website/insurance_forms.py` — quote + purchase forms
- `website/insurance_views.py` — views
- `website/models.py` — `TravelInsuranceOrder`
