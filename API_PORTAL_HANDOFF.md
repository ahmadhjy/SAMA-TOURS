# Sama Tours API handoff: Monty eSIM and Swan IMS travel insurance

This is a code-based implementation handoff for another Sama Tours Django portal. It describes the **current local integration**, not an authorization to issue live products. Both services are restricted to staff on this website (`website/urls.py`); no public checkout or payment gateway is connected. Do not copy credentials from the current server, browser, or old documents into the new portal. Obtain separate production credentials and account permissions from the providers.

## Source of truth in this repository

- Monty API specification: `docs/monty-esim-openapi.json`; provider flow: `docs/Monty eSIM Reseller Integration Flow - Copy 1 1 (1).pdf`.
- Swan collection: `docs/ims-v5-api.postman_collection.json`.
- Running code: `website/monty_esim.py`, `website/esim_filters.py`, `website/views.py`, `website/forms.py`, `website/swan_ims.py`, `website/insurance_forms.py`, `website/insurance_filters.py`, `website/insurance_plans.py`, `website/insurance_views.py`.
- Database: `EsimOrder` and `TravelInsuranceOrder` in `website/models.py`; migration history in `website/migrations/0011_esim_order.py` and `0012_travel_insurance_order.py`.
- UI: `templates/website/esim*.html`, `templates/website/insurance*.html`, `templates/includes/esim*.html`, `templates/includes/insurance*.html`, `static/js/esim.js`, `static/js/insurance.js`. EN/AR/FR strings are in `scripts/build_locales.py` and `locale/*`.

## Monty eSIM

### Configuration and authentication

Default API base: `https://resellerapi.montyesim.com/api/v0`. Portal: `https://reseller.montyesim.com/`. Environment variables: `MONTY_ESIM_API_BASE_URL`, `MONTY_ESIM_PORTAL_URL`, `MONTY_ESIM_USERNAME`, `MONTY_ESIM_PASSWORD`, `MONTY_ESIM_CURRENCY` (default `USD`). `POST /Agent/login` receives JSON `username` and `password`; response supplies `access_token`, `refresh_token`, `reseller_id`, `expires_in`. Code caches the session and uses `POST /Token/Refresh` when possible. Protected calls try `Access-Token` header, then Bearer authorization on 401/403. Do not expose tokens, passwords or QR activation codes to client-side logs.

### Catalog and filtering

- `GET /AvailableCountries` and `GET /AvailableRegions` with `reseller_id`; current code caches these for one hour.
- `GET /Bundles` with `reseller_id`, `page_number`, `page_size` (50 in current UI), `currency_code`, optional `bundle_category`, `country_code`, `region_code`, `sort_by`, `bundle_name`, `profile_type`. Response keys used: `bundles`, `total_bundles_count`.
- `website/esim_filters.py` adds client-side filters for destination/region, name, category, profile, min/max price, validity/data and sorting. The UI supports Load More; never assume the first 50 are the full catalog.
- Display helpers in `monty_esim.py` map names, country, data and prices. Retail pricing and settlement rules should be confirmed with Monty; `currency_code=USD` is a request, not a currency conversion guarantee.

### Order lifecycle

1. Collect bundle code, customer name/email and optional WhatsApp. Create a local unique reference.
2. `POST /Bundles` with `reseller_id`, `currency_code` query parameters and JSON `bundle_code`, `email`, `name`, `order_reference`, optional `whatsapp_number`. **This is a live billable action** on a live account. A new portal must take customer payment and verify it server-side before calling this endpoint; build idempotency and retry handling so a timeout cannot double-charge.
3. Read `order_id` from response. `GET /Orders` filtered by `reseller_id` and `order_id`; `activation_code` is the eSIM installation/QR payload. Current code polls up to six times with 1.5-second spacing.
4. Save `EsimOrder` with local reference, Monty ID, bundle details, customer contact, ICCID, activation code, price, status and message. Current success page renders QR from activation code; QR view checks session access. Lookup uses email plus local reference. `POST /Orders/ResendEmail` can request a provider resend.
5. Reconcile order state and reseller balance in the Monty portal. Refunds are handled by Monty after submitting an order ID and eligibility review; there is no guaranteed automatic refund path in this code.

The current code calls Monty directly before any payment processing; **do not copy that checkout behavior into a public portal**. Treat displayed price as informational until payment and fulfillment are designed together.

## Swan / Cygnet IMS v5 travel insurance

### Configuration and authentication

Current default API base is staging `https://staging.cygnet-ims.com/`. Environment variables: `SWAN_IMS_API_BASE_URL`, `SWAN_IMS_USERNAME`, `SWAN_IMS_PASSWORD`, `SWAN_IMS_SANDBOX`, `SWAN_IMS_ALLOW_CHECKOUT`, `SWAN_IMS_DEFAULT_RESIDENCE` (default `LBN`). `POST /api/v5/login` authenticates, then code reads access token, tenant ID and agency ID from response and caches them. Subsequent calls use `Authorization: Bearer <token>` and `Tenant: <tenant_id>`; agency ID is sent in quote and contract JSON. Never infer live availability from sandbox results. Ask SIA/Swan for production URL and credentials and confirm agency product permissions.

### Quote and plan details

1. Quote form collects residence country (ISO3), destination (ISO3), departure/return dates, traveler count and each traveler's birth date; forms validate date order and required ages.
2. `POST /api/v5/travel/plans` with `country` (residence), `agency`, `destinations: [{country, from_date, till_date}]` and `travellers` per `InsuranceQuoteForm`. Only plans enabled and priced for those inputs appear; the UI does not have a complete static product catalog.
3. `flatten_plan_offers` and `website/insurance_plans.py` convert raw plan structures into displayed offers, benefit/exclusion lists and deductible-tier prices. Preserve the API's currency (`AUD` can occur) rather than relabeling or converting without a rate source. Client-side filters include tier, COVID/sports, currency and price. The AJAX quote endpoint updates results without a full page reload.
4. Recheck selected plan and `price_ids` against a fresh server-side quote before issuing a contract in a new portal; current form carries selection data from the page. Treat this as essential checkout hardening.

### Contract lifecycle

1. Collect email, phone, address, selected plan/tier and full traveler details required by the API. `InsurancePurchaseForm.travellers_payload` builds API travelers, including selected per-person price IDs.
2. `POST /api/v5/travel/contract` with `country`, `agency`, `plan_id`, `phone`, `email`, `address`, `destinations` and `travellers`. **Contract creation may issue a real policy in production.** Confirm payment before making this call and coordinate cancellation/refund behavior with SIA.
3. Extract contract code; save `TravelInsuranceOrder` with local reference, contract code, plan, exact price/currency, trip, customer contact and traveler JSON. The local lookup uses email plus reference.
4. `GET /api/v5/travel/contract/pdf?code=<code>` downloads the policy. `POST /api/v5/travel/contract/email` with `code`, `email`, `attachments: [contract, receipt, general_conditions]` asks the provider to email policy documents. PDF and order views require authorized session access in current code.

### Operational guardrails for the new portal

- Keep `SWAN_IMS_ALLOW_CHECKOUT=False` until live account permissions and payment verification exist. Keep the sandbox flag accurate for the environment.
- Design a payment state machine (`pending payment → paid → provider request → issued/failed`) with unique order references, retries, reconciliation and an operator queue for uncertain provider responses. Never automatically retry a billable POST after an ambiguous timeout without checking provider state.
- Provider APIs and credentials stay on the server. Rate-limit quote and purchase endpoints; validate payloads, log references/status without sensitive traveler or payment data, and restrict PDF/QR access to the owner or staff.
- Do not store passport or traveler identity fields longer than required by the business/legal retention policy; protect database backups and admin accounts.
- Test catalog, quote, payment success/failure, provider timeout, duplicate submit, QR/PDF retrieval, email resend and EN/AR/FR display using mocked API responses. Sandbox may create test policies; live Monty requests can debit the account.
- Configure the new portal's environment variables independently. Reuse code ideas, not shared production credentials or database tables. Verify provider contract and permission to use one reseller account across both portals.
