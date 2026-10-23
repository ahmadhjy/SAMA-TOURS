from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import FlightMatchRequest
from .private_storage import flight_match_storage


def screenshot(name='offer.png'):
    output = BytesIO()
    Image.new('RGB', (24, 24), 'blue').save(output, 'PNG')
    return SimpleUploadedFile(name, output.getvalue(), content_type='image/png')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class FlightMatchTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(dir=settings.BASE_DIR)
        old_location = flight_match_storage.location
        flight_match_storage.location = self.directory.name
        self.addCleanup(setattr, flight_match_storage, 'location', old_location)
        self.addCleanup(self.directory.cleanup)
        self.url = reverse('website:flight_match')

    def payload(self, **updates):
        data = {
            'email': 'test@example.com', 'phone': '', 'passengers': 1,
            'consent': 'on', 'price_confirmed': 'on', 'payment_preference': 'omt',
            'screenshot': [screenshot('offer1.png'), screenshot('offer2.png')],
            'passport': [screenshot('passport1.png'), screenshot('passport2.png')],
        }
        data.update(updates)
        return data

    def test_multiple_files_saved_and_emailed_without_name_or_price(self):
        response = self.client.post(self.url, self.payload())
        self.assertEqual(response.status_code, 302)
        match = FlightMatchRequest.objects.get()
        self.assertTrue(match.notification_sent)
        self.assertEqual(match.full_name, '')
        self.assertIsNone(match.offered_price)
        self.assertIn('OMT Cash', match.notes)
        self.assertEqual(match.attachments.count(), 2)
        for doc in [match.screenshot, match.passport] + [a.document for a in match.attachments.all()]:
            self.assertTrue(doc.storage.exists(doc.name))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(len(mail.outbox[0].attachments), 4)
        self.assertEqual(mail.outbox[0].to, [settings.FLIGHT_MATCH_RECIPIENT])
        self.assertEqual(mail.outbox[0].reply_to, ['test@example.com'])

    def test_files_require_staff_and_admin_shows_additional_files(self):
        self.client.post(self.url, self.payload())
        match = FlightMatchRequest.objects.get()
        urls = [
            reverse('website:flight_match_file', args=[match.pk, 'passport']),
            reverse('website:flight_match_attachment_file', args=[match.attachments.first().pk]),
        ]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)
        user = get_user_model().objects.create_user('viewer', password='test-pass')
        self.client.force_login(user)
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 302)
        user.is_staff = user.is_superuser = True
        user.save()
        for url in urls:
            download = self.client.get(url)
            self.assertEqual(download.status_code, 200)
            self.assertIn('attachment', download['Content-Disposition'])
            download.close()
        admin = self.client.get(reverse('admin:website_flightmatchrequest_change', args=[match.pk]))
        self.assertEqual(admin.status_code, 200)
        self.assertContains(admin, urls[1])

    def test_phone_only_and_both_contacts_are_valid(self):
        for email in ['', 'test@example.com']:
            response = self.client.post(self.url, self.payload(email=email, phone='+96170000000'))
            self.assertEqual(response.status_code, 302)
        self.assertEqual(FlightMatchRequest.objects.count(), 2)

    def test_requires_one_contact_method(self):
        response = self.client.post(self.url, self.payload(email='', phone=''))
        self.assertEqual(response.status_code, 200)
        self.assertIn('__all__', response.context['form'].errors)
        self.assertFalse(FlightMatchRequest.objects.exists())

    def test_passport_offer_and_confirmation_required(self):
        for field in ['passport', 'screenshot', 'price_confirmed']:
            data = self.payload()
            data.pop(field)
            response = self.client.post(self.url, data)
            self.assertEqual(response.status_code, 200)
            self.assertIn(field, response.context['form'].errors)
        self.assertFalse(FlightMatchRequest.objects.exists())

    def test_every_file_is_validated(self):
        response = self.client.post(self.url, self.payload(
            passport=[screenshot(), SimpleUploadedFile('fake.png', b'not an image')],
        ))
        self.assertEqual(response.status_code, 200)
        self.assertIn('passport', response.context['form'].errors)
        self.assertFalse(FlightMatchRequest.objects.exists())

    def test_limits_file_count_and_combined_size(self):
        response = self.client.post(self.url, self.payload(screenshot=[screenshot() for _ in range(6)]))
        self.assertIn('screenshot', response.context['form'].errors)
        files = [SimpleUploadedFile('test.pdf', b'%PDF-1.4\n' + b'0' * (6 * 1024 * 1024)) for _ in range(3)]
        response = self.client.post(self.url, self.payload(screenshot=files))
        self.assertIn('__all__', response.context['form'].errors)
        response = self.client.post(self.url, self.payload(
            passport=[SimpleUploadedFile('large.pdf', b'%PDF-1.4\n' + b'0' * (8 * 1024 * 1024))],
        ))
        self.assertIn('passport', response.context['form'].errors)
        self.assertFalse(FlightMatchRequest.objects.exists())

    @patch('website.flight_match.EmailMessage.send', side_effect=RuntimeError('Test mail failure'))
    def test_email_failure_keeps_request_and_all_uploads(self, send):
        response = self.client.post(self.url, self.payload(), follow=True)
        match = FlightMatchRequest.objects.get()
        self.assertFalse(match.notification_sent)
        self.assertEqual(match.attachments.count(), 2)
        self.assertContains(response, match.reference)
        self.assertTrue(match.passport.storage.exists(match.passport.name))

    def test_reference_sections_and_languages(self):
        for lang, heading in [('en', 'Sama Match Request Form'), ('ar', 'نموذج طلب سما ماتش'), ('fr', 'Formulaire Sama Match')]:
            response = self.client.get('/' + lang + '/sama-match/')
            self.assertContains(response, heading)
            for section in ['payments', 'comparison', 'how-it-works', 'faq']:
                self.assertContains(response, 'id="' + section + '"')
            self.assertNotContains(response, 'name="full_name"')
            self.assertNotContains(response, 'name="offered_price"')
            self.assertContains(response, 'multiple required', count=2)
            self.assertContains(response, 'id="language-picker"')

    def test_homepage_sama_match_button_in_all_languages(self):
        for lang in ['en', 'ar', 'fr']:
            response = self.client.get('/' + lang + '/')
            self.assertContains(response, 'href="/' + lang + '/sama-match/" class="btn btn-lg btn-sama-match"')
