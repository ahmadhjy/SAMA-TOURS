# Monty eSIM integration — Sama Tours

Guide for adding **travel eSIM** to [samatourslb.com](https://www.samatourslb.com) using Monty Mobile’s **Reseller API**.

**API docs (login required):** [https://resellerapi.montyesim.com/api/v0/ui/](https://resellerapi.montyesim.com/api/v0/ui/)

---

## What Monty offers (3 options)

| Option | Best for | Effort | Customer experience |
|--------|----------|--------|---------------------|
| **A. Reseller Portal only** | Staff sell eSIMs manually; no website change | Low | Customer gets QR by email; team uses Monty portal |
| **B. White-label / iframe store** | Fast launch, Monty-hosted checkout | Medium | Branded shop embedded on your site |
| **C. Full REST API** | Full control, same look as Sama Tours site | High | Browse plans → pay → QR on your site |

For **Sama Tours**, a practical rollout is usually:

1. **Phase 1** — eSIM info page + WhatsApp / contact (can go live immediately).
2. **Phase 2** — Reseller Portal for staff + link from website.
3. **Phase 3** — API or iframe shop when credentials and pricing are finalized.

---

## Recommended architecture (Phase 3 — API)

Monty’s reseller flow typically looks like this (exact endpoints are in your Swagger UI after login):

```
Visitor (EN/AR/FR site)
    → Browse destinations / data bundles (cached from Monty API)
    → Select plan + enter email (eSIM delivery)
    → Checkout (your payment OR Monty wallet / reseller balance)
    → Monty creates order → returns QR / activation details
    → Email to customer + optional order history in Django admin
```

**Backend (Django):**

- `website/monty_esim/` or `website/services/monty.py` — API client (auth, bundles, orders).
- Server-side only for **API keys** — never expose secrets in templates/JS.
- Optional: cache bundle catalog (Redis or DB + cron) to avoid slow pages.
- Store orders locally (`EsimOrder`) for support and reconciliation.

**Frontend:**

- New pages: `/en/esim/`, `/ar/esim/`, `/fr/esim/` (same i18n pattern as packages/visa).
- Nav link: **eSIM** or **Travel eSIM**.
- Reuse existing design (hero, cards, WhatsApp CTA as fallback).

**Payments (decide with Monty):**

- **Reseller wallet** — you prepay Monty; orders deduct balance (common for agencies).
- **Customer pays you** — Stripe/local gateway on your site, then you call Monty API to fulfill.
- **Monty checkout** — if they provide a hosted payment URL (ask on the call).

---

## What to request from Monty **before** development

Reply to support and ask for:

1. **Reseller portal login** (if not already provisioned).
2. **API credentials**
   - Sandbox / staging base URL (if different from production).
   - Production base URL.
   - Authentication method (API key header name, OAuth, client ID/secret, etc.).
3. **Swagger / OpenAPI export** — JSON or PDF if the UI is hard to share.
4. **Sandbox test account** with test bundles and test orders.
5. **Webhooks** — order status, activation, refunds (URLs you must expose).
6. **Pricing model** — wholesale cost, recommended retail, who sets end-user price.
7. **Settlement** — invoicing, minimum top-up, currency (USD/LBP).
8. **Branding** — can QR emails use Sama Tours logo and `info@samatourslb.com`?
9. **Compliance** — terms you must show on the site (refund policy, device compatibility).
10. **Rate limits** and expected latency for catalog + order endpoints.

---

## Questions for the technical call

### API & auth

- Which endpoints list **available bundles** (by country/region)?
- How do we **create an order** (required fields: email, SKU, quantity)?
- How is the **eSIM QR** returned (API response, email only, webhook)?
- Is there an **order status** endpoint and idempotency for retries?
- Sandbox vs production — same paths, different keys?

### Business flow

- Do we sell from a **prepaid reseller balance** or per-order billing?
- Can we set **our own retail prices** on top of wholesale?
- Refunds and failed activations — process and API support?
- Multi-quantity / family plans?

### Website integration

- Do you provide a **white-label URL** or **iframe embed** for faster launch?
- Any **JavaScript SDK** for bundle listing, or REST only?
- **CORS** — must all calls go through our server (expected for Django)?

### Operations

- SLA and support channel for failed orders.
- Reporting API or portal export for accounting.
- Device compatibility list — can we embed it on our FAQ?

---

## Environment variables (when API is ready)

Add to `deploy/production.env` (never commit real values):

```bash
# Monty eSIM Reseller API
MONTY_ESIM_API_BASE_URL=https://resellerapi.montyesim.com/api/v0
MONTY_ESIM_API_KEY='your-api-key'
# MONTY_ESIM_API_SECRET='if-applicable'
MONTY_ESIM_SANDBOX=true
```

Wire in `config/settings/base.py` via `_env()` like other secrets.

---

## Phase 1 — Launch without API (optional, ~1 day)

You can add an **eSIM landing page** now while waiting for API access:

- Explain benefits (stay connected abroad, no physical SIM, instant QR).
- Popular destinations (Europe, GCC, Turkey, etc.) — static or from admin later.
- **Primary CTA:** WhatsApp with pre-filled message (“I need an eSIM for …”).
- **Secondary:** Contact form / email.

This matches how packages started (WhatsApp-first) and avoids blocking on Monty credentials.

**Site changes (when you approve build):**

- `website/urls.py` → `path('esim/', views.esim, name='esim')`
- `templates/website/esim.html`
- Nav + footer link
- Strings in `scripts/build_locales.py` for AR/FR

---

## Phase 3 — Django implementation checklist

When you have API docs + sandbox keys:

- [ ] API client module + unit tests with mocked responses
- [ ] Settings + env vars on PythonAnywhere
- [ ] `EsimOrder` model (Monty order id, email, bundle, status, QR reference)
- [ ] Views: catalog, plan detail, checkout POST (server-side)
- [ ] Admin: view orders, retry failed fulfillment
- [ ] Templates EN/AR/FR + translations
- [ ] Error handling + user-friendly messages
- [ ] Logging (no secrets in logs)
- [ ] Webhook endpoint (HTTPS, CSRF exempt, signature verification if provided)
- [ ] Update `CONTENT_ADMIN_GUIDE.md` if any content is managed in admin

---

## Draft reply to Monty support

You can copy/adapt this:

> Dear [Name],
>
> Thank you for sharing the API documentation link.
>
> We are planning to integrate Monty eSIM into our travel agency website (**Sama Tours** — [https://www.samatourslb.com](https://www.samatourslb.com)), which is a Django site with English, Arabic, and French.
>
> Our technical team will review the documentation at  
> [https://resellerapi.montyesim.com/api/v0/ui/](https://resellerapi.montyesim.com/api/v0/ui/)  
> and we would appreciate a short technical call to confirm:
>
> - API authentication and sandbox credentials  
> - Endpoints for bundle catalog and order creation  
> - How the eSIM QR / activation is delivered to the end customer  
> - Reseller billing model (prepaid wallet vs per order) and pricing flexibility  
> - Whether a white-label or iframe storefront is available for a faster first launch  
>
> Please advise available times for a call and confirm what credentials we should expect (portal user, API keys, sandbox environment).
>
> Best regards,  
> Ali [Surname]  
> Sama Tours

---

## Security notes

- Store API keys only in **environment variables** on PythonAnywhere.
- All Monty API calls from **Django backend**, not from the browser.
- Validate email and bundle IDs server-side before creating orders.
- Use HTTPS only; add webhook path to `CSRF_TRUSTED_ORIGINS` if needed.
- Do not log full API keys or QR payload secrets.

---

## Next step for you

1. **Log in** to the Swagger UI and skim: auth, bundles, orders (or export OpenAPI).
2. **Send** the draft email above (or schedule the call).
3. **Tell us** which phase you want built first:
   - **Phase 1** — marketing page + WhatsApp only  
   - **Phase 2** — link to Monty reseller portal  
   - **Phase 3** — full API integration (needs sandbox keys)

Once you have sandbox credentials or an OpenAPI export, we can implement the API client and eSIM pages on the site.
