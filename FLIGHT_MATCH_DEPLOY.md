# Sama Match deployment notes

The new route is `/en/sama-match/` (also `/ar/sama-match/` and `/fr/sama-match/`). The existing PythonAnywhere update script applies migration `0014`, collects CSS and builds translations. It does **not** set up an email account.

Before publishing the form, edit `/home/Samatours2026/SAMA-TOURS/deploy/production.env` on PythonAnywhere. Add `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `EMAIL_USE_SSL`, `DEFAULT_FROM_EMAIL`, `FLIGHT_MATCH_TO_EMAIL`. Use the SMTP host and an app password provided by the mailbox host. The recipient defaults to `info@samatourslb.com`. Do not commit these values. Keep `EMAIL_USE_TLS=True` for port 587, or use `EMAIL_USE_SSL=True` and `EMAIL_USE_TLS=False` for port 465 if that is what the provider specifies.

Update command in PythonAnywhere Bash:

```bash
cd ~/SAMA-TOURS && bash deploy/update.sh
```

If `PA_WSGI_FILE` is not configured, click **Reload** on the website's Web tab. Confirm migration `website.0014` and CSS collection succeeded. Submit one test request with a small screenshot and a contact method. Check the recipient inbox/spam folder and the **Flight match requests** admin list. Verify the screenshot downloads only while logged in as staff. Uploads are stored in `private_uploads/` outside the public `media/` mapping; include this directory in secure backups and restrict filesystem access. Set a retention period for passports and remove requests/files when no longer needed.

The supplied concept HTML was not deployed directly. It simulates PNR creation and payments, uses a placeholder WhatsApp number, and promises fares/timings the current platform cannot guarantee. This implementation accepts a manual comparison request only.
