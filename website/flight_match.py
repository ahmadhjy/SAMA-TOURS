import logging
import mimetypes
from pathlib import Path
from uuid import uuid4

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import EmailMessage, get_connection
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _, gettext_lazy, get_language

from .models import FlightMatchRequest, FlightMatchAttachment

logger = logging.getLogger(__name__)


def validate_upload(upload):
    from PIL import Image, UnidentifiedImageError

    if upload.size > 8 * 1024 * 1024:
        raise forms.ValidationError(_('Each file must be smaller than 8 MB.'))
    header = upload.read(12)
    upload.seek(0)
    if header.startswith(b'%PDF-'):
        if not upload.name.lower().endswith('.pdf'):
            raise forms.ValidationError(_('Use a PDF, JPG, PNG or WebP file.'))
        return
    try:
        image = Image.open(upload)
        image.verify()
        image_type = image.format
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise forms.ValidationError(_('Use a PDF, JPG, PNG or WebP file.')) from exc
    finally:
        upload.seek(0)
    suffix = upload.name.lower().rsplit('.', 1)[-1]
    if image_type not in {'JPEG', 'PNG', 'WEBP'} or suffix not in {'jpg', 'jpeg', 'png', 'webp'}:
        raise forms.ValidationError(_('Use a PDF, JPG, PNG or WebP file.'))


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        files = data if isinstance(data, (list, tuple)) else [data]
        if len(files) > 5:
            raise forms.ValidationError(_('Upload up to 5 files per section.'))
        cleaned = []
        for upload in files:
            upload = super().clean(upload, initial)
            validate_upload(upload)
            cleaned.append(upload)
        if not cleaned:
            raise forms.ValidationError(self.error_messages['required'])
        return cleaned


class FlightMatchForm(forms.Form):
    email = forms.EmailField(required=False)
    phone = forms.CharField(required=False, max_length=40)
    passengers = forms.IntegerField(min_value=1, max_value=20)
    screenshot = MultipleFileField()
    passport = MultipleFileField()
    consent = forms.BooleanField(label=gettext_lazy('I agree to share these details with Sama Tours for this flight request.'))
    price_confirmed = forms.BooleanField(label=gettext_lazy('Total price visible'))
    payment_preference = forms.ChoiceField(choices=(
        ('whish', 'Whish Money'), ('omt', 'OMT Cash'), ('card_link', 'Card Link'),
    ))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .flight_match_copy import COPY
        copy = COPY.get(get_language(), COPY['en'])
        for field, key in {
            'phone': 'labelWhatsApp', 'email': 'emailLabel',
            'passport': 'labelPassport', 'screenshot': 'labelScreenshot',
            'passengers': 'labelPax', 'payment_preference': 'labelPayPref',
            'price_confirmed': 'checkboxConfirmPrice',
        }.items():
            self.fields[field].label = strip_tags(copy[key]).rstrip(' *')

    def clean(self):
        data = super().clean()
        if not data.get('email') and not data.get('phone'):
            raise forms.ValidationError(_('Please enter an email address or phone number.'))
        uploads = data.get('screenshot', []) + data.get('passport', [])
        if sum(upload.size for upload in uploads) > 15 * 1024 * 1024:
            raise forms.ValidationError(_('The combined size of all files must not exceed 15 MB.'))
        return data


def match_mail_connection():
    return get_connection(
        backend=settings.EMAIL_BACKEND,
        host=settings.FLIGHT_MATCH_SMTP_HOST,
        port=settings.FLIGHT_MATCH_SMTP_PORT,
        username=settings.FLIGHT_MATCH_SMTP_USER,
        password=settings.FLIGHT_MATCH_SMTP_PASSWORD,
        use_tls=settings.FLIGHT_MATCH_SMTP_TLS,
        use_ssl=settings.FLIGHT_MATCH_SMTP_SSL,
        timeout=settings.EMAIL_TIMEOUT,
    )


def notify_match(match, admin_url):
    body = (
        f'New flight match request {match.reference}\n\n'
        f'Email: {match.email or "—"}\nWhatsApp: {match.phone or "—"}\n'
        f'Passengers: {match.passengers}\n{match.notes}\n\n'
        f'Offer and passport files are attached and also saved privately in Django Admin.\n'
        f'Open request: {admin_url}\n'
    )
    message = EmailMessage(
        f'Sama Match request {match.reference}', body,
        settings.FLIGHT_MATCH_FROM_EMAIL, [settings.FLIGHT_MATCH_RECIPIENT],
        reply_to=[match.email] if match.email else [],
        connection=match_mail_connection(),
    )
    documents = [('screenshot', match.screenshot), ('passport', match.passport)]
    documents += [(item.kind, item.document) for item in match.attachments.all()]
    for index, (kind, document) in enumerate(documents, start=1):
        filename = f'{match.reference}-{kind}-{index}{Path(document.name).suffix}'
        with document.open('rb') as uploaded:
            message.attach(filename, uploaded.read(), mimetypes.guess_type(filename)[0] or 'application/octet-stream')
    if message.send(fail_silently=False) != 1:
        raise RuntimeError('Email backend did not confirm delivery')


def flight_match(request):
    form = FlightMatchForm(request.POST if request.method == 'POST' else None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        saved_documents = []
        try:
            with transaction.atomic():
                match = FlightMatchRequest(
                    reference=f'SM-{uuid4().hex[:10].upper()}',
                    email=data['email'], phone=data['phone'], passengers=data['passengers'],
                    notes='Preferred payment: ' + dict(form.fields['payment_preference'].choices)[data['payment_preference']]
                          + '\nTotal price visible in screenshot: confirmed'
                          + ('\nPassenger selection: 4+ family/group' if data['passengers'] == 4 else ''),
                )
                for kind in ('screenshot', 'passport'):
                    upload = data[kind][0]
                    document = getattr(match, kind)
                    document.save(upload.name, upload, save=False)
                    saved_documents.append(document)
                match.save()
                for kind in ('screenshot', 'passport'):
                    for upload in data[kind][1:]:
                        attachment = FlightMatchAttachment(request=match, kind=kind)
                        attachment.document.save(upload.name, upload, save=False)
                        saved_documents.append(attachment.document)
                        attachment.save()
        except Exception:
            # Only files created for this failed transaction are removed.
            for document in saved_documents:
                document.storage.delete(document.name)
            raise
        admin_url = request.build_absolute_uri(reverse('admin:website_flightmatchrequest_change', args=[match.pk]))
        try:
            notify_match(match, admin_url)
        except Exception:
            logger.exception('Flight match email failed for reference %s', match.reference)
            messages.error(request, _('Your request was saved, but email delivery failed. Please contact Sama Tours with your reference number: %(reference)s') % {'reference': match.reference})
        else:
            match.notification_sent = True
            match.save(update_fields=['notification_sent'])
            messages.success(request, _('Your flight request was received. Reference: %(reference)s. Our team will review it and contact you.') % {'reference': match.reference})
        return redirect('website:flight_match')
    from .flight_match_copy import COPY
    return render(request, 'website/flight_match.html', {
        'form': form, 'match_copy': COPY.get(get_language(), COPY['en']),
    })


@staff_member_required
def flight_match_file(request, pk, kind):
    match = get_object_or_404(FlightMatchRequest, pk=pk)
    if kind not in ('screenshot', 'passport'):
        raise Http404
    document = getattr(match, kind)
    if not document:
        raise Http404
    return FileResponse(
        document.open('rb'), as_attachment=True,
        filename=f'{match.reference}-{kind}{Path(document.name).suffix}',
    )


@staff_member_required
def flight_match_attachment_file(request, pk):
    attachment = get_object_or_404(FlightMatchAttachment.objects.select_related('request'), pk=pk)
    return FileResponse(
        attachment.document.open('rb'), as_attachment=True,
        filename=f'{attachment.request.reference}-{attachment.kind}-{attachment.pk}{Path(attachment.document.name).suffix}',
    )
