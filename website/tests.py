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
        })
        self.assertEqual(response.status_code, 302)
        match = FlightMatchRequest.objects.get()
        self.assertTrue(match.notification_sent)
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
