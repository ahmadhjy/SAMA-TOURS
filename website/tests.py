from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import FlightMatchRequest
from .private_storage import flight_match_storage


def screenshot():
    output = BytesIO()
    Image.new('RGB', (24, 24), 'blue').save(output, 'PNG')
    return SimpleUploadedFile('offer.png', output.getvalue(), content_type='image/png')


class FlightMatchTests(TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory(dir=settings.BASE_DIR)
        flight_match_storage.location = self.directory.name
        self.addCleanup(self.directory.cleanup)
        self.url = reverse('website:flight_match')

    @override_settings(EMAIL_HOST='smtp.example.com', EMAIL_HOST_USER='sender@example.com')
    @patch('website.flight_match.send_mail', return_value=1)
    def test_submission_saves_private_file_and_notifies(self, send_mail):
        response = self.client.post(self.url, {
            'full_name': 'Ada Example', 'email': 'ada@example.com', 'phone': '',
            'passengers': 1, 'consent': 'on', 'screenshot': screenshot(),
            'passport': screenshot(), 'price_confirmed': 'on',
            'payment_preference': 'omt', 'offered_price': '540',
        })
        self.assertEqual(response.status_code, 302)
        match = FlightMatchRequest.objects.get()
        self.assertTrue(match.notification_sent)
        self.assertEqual(match.offered_currency, 'USD')
        self.assertIn('OMT Cash', match.notes)
        self.assertTrue(match.passport)
        self.assertTrue(match.screenshot.storage.exists(match.screenshot.name))
        send_mail.assert_called_once()
        file_url = reverse('website:flight_match_file', args=[match.pk, 'screenshot'])
        self.assertEqual(self.client.get(file_url).status_code, 302)
        user = get_user_model().objects.create_user('staff', password='test-pass', is_staff=True)
        self.client.force_login(user)
        download = self.client.get(file_url)
        self.assertEqual(download.status_code, 200)
        download.close()

    def test_requires_contact_method(self):
        response = self.client.post(self.url, {
            'full_name': 'Ada Example', 'email': '', 'phone': '',
            'passengers': 1, 'consent': 'on', 'screenshot': screenshot(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FlightMatchRequest.objects.exists())

    def test_rejects_invalid_file(self):
        response = self.client.post(self.url, {
            'full_name': 'Ada Example', 'email': 'ada@example.com',
            'passengers': 1, 'consent': 'on',
            'screenshot': SimpleUploadedFile('fake.png', b'not an image'),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(FlightMatchRequest.objects.exists())

    def test_passport_and_price_confirmation_are_required(self):
        from .flight_match import FlightMatchForm
        form = FlightMatchForm({
            'full_name': 'Ada Example', 'email': 'ada@example.com',
            'passengers': 1, 'consent': 'on', 'offered_price': '540',
            'payment_preference': 'whish',
        }, {'screenshot': screenshot()})
        self.assertFalse(form.is_valid())
        self.assertIn('passport', form.errors)
        self.assertIn('price_confirmed', form.errors)

    def test_phone_only_is_valid_and_unknown_payment_rejected(self):
        from .flight_match import FlightMatchForm
        data = {
            'full_name': 'Ada Example', 'phone': '+96170000000',
            'passengers': 2, 'consent': 'on', 'offered_price': '540.50',
            'payment_preference': 'card_link', 'price_confirmed': 'on',
        }
        form = FlightMatchForm(data, {'screenshot': screenshot(), 'passport': screenshot()})
        self.assertTrue(form.is_valid(), form.errors)
        data['payment_preference'] = 'unsupported'
        form = FlightMatchForm(data, {'screenshot': screenshot(), 'passport': screenshot()})
        self.assertFalse(form.is_valid())
        self.assertIn('payment_preference', form.errors)

    def test_reference_sections_and_languages(self):
        for lang, heading in [('en', 'Sama Match Request Form'), ('ar', 'نموذج طلب سما ماتش'), ('fr', 'Formulaire Sama Match')]:
            response = self.client.get('/' + lang + '/sama-match/')
            self.assertContains(response, heading)
            for section in ['payments', 'comparison', 'how-it-works', 'faq']:
                self.assertContains(response, 'id="' + section + '"')
            self.assertNotContains(response, 'Passport upload is optional')
            self.assertNotContains(response, 'cdn.tailwindcss.com')
