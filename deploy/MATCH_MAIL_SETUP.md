# Sama Match mailbox setup

The app saves requests and every uploaded file privately in Django Admin, then
emails all files to the configured Sama Match inbox. An SMTP failure leaves the
saved request available in Admin, with notification_sent=False and a visible
warning/reference for the customer.

## One-time PythonAnywhere setup

1. Upload the private local file deploy/match-mail.env using PythonAnywhere's
   Files tab to /home/Samatours2026/SAMA-TOURS/deploy/match-mail.env.
   Alternatively copy match-mail.env.example to match-mail.env and set the password.
2. In Bash:

   cd ~/SAMA-TOURS
   chmod 600 deploy/match-mail.env
   bash deploy/update.sh

3. Reload the WEBSITE web app, not the ERP.

Settings load this file for both WSGI and management commands. No WSGI edits
are needed. Environment variables take precedence over file values.
This dedicated configuration does not replace the ERP or other service settings.
The private file is ignored by Git; never upload it to GitHub.

SMTP: smtp.ionos.com, port 587, STARTTLS, authenticated as match@samatourslb.com.
Sender and recipient: match@samatourslb.com.

## Verification

Submit a request with synthetic offer/passport files. Verify it appears in
Django Admin and that the mailbox receives every attachment. Only staff can
download files through the app; private_uploads must never be a public static
or media mapping. Back up private_uploads with the database.

Limits: five files per section, 8 MB per file, 15 MB combined (before email
encoding). Both offer and passport sections require at least one file.
Either email or phone is required; both are accepted. No price/name entry.

Migration 0015 adds an attachment table and makes the legacy name optional.
Existing requests and primary files are preserved; no backfill is necessary.

To rotate the password later, edit only FLIGHT_MATCH_SMTP_PASSWORD in the
private file and reload the website.
