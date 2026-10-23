import logging
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _, gettext_lazy, get_language

from .models import FlightMatchRequest

logger = logging.getLogger(__name__)


class FlightMatchForm(forms.ModelForm):
    consent = forms.BooleanField(label=gettext_lazy('I agree to share these details with Sama Tours for this flight request.'))
    price_confirmed = forms.BooleanField(label=gettext_lazy('Total price visible'))
    payment_preference = forms.ChoiceField(choices=(
        ('whish', 'Whish Money'), ('omt', 'OMT Cash'), ('card_link', 'Card Link'),
    ))
    offered_price = forms.DecimalField(max_digits=10, decimal_places=2, min_value=Decimal('0.01'))
    passengers = forms.IntegerField(min_value=1, max_value=20)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['passport'].required = True
        from .flight_match_copy import COPY
        copy = COPY.get(get_language(), COPY['en'])
        for field, key in {
            'full_name': 'labelFullName', 'phone': 'labelWhatsApp',
            'email': 'emailLabel', 'passport': 'labelPassport',
            'screenshot': 'labelScreenshot', 'offered_price': 'labelPriceSeen',
            'passengers': 'labelPax', 'payment_preference': 'labelPayPref',
            'price_confirmed': 'checkboxConfirmPrice',
        }.items():
            self.fields[field].label = strip_tags(copy[key]).rstrip(' *')

    class Meta:
        model = FlightMatchRequest
        fields = ('full_name', 'email', 'phone', 'route', 'travel_dates', 'offered_price', 'offered_currency', 'passengers', 'notes', 'screenshot', 'passport')
        widgets = {
            'full_name': forms.TextInput(attrs={'autocomplete': 'name'}),
            'email': forms.EmailInput(attrs={'autocomplete': 'email'}),
            'phone': forms.TextInput(attrs={'autocomplete': 'tel'}),
            'passengers': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'offered_price': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'screenshot': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/webp,application/pdf'}),
            'passport': forms.ClearableFileInput(attrs={'accept': 'image/jpeg,image/png,image/webp,application/pdf'}),
        }

    def clean(self):
        data = super().clean()
        if not data.get('email') and not data.get('phone'):
            raise forms.ValidationError(_('Please enter an email address or phone number.'))
        data['offered_currency'] = 'USD'
        return data

    def _check_upload(self, field):
        from PIL import Image, UnidentifiedImageError

        upload = self.cleaned_data.get(field)
        if not upload:
            return upload
        if upload.size > 8 * 1024 * 1024:
            raise forms.ValidationError(_('Each file must be smaller than 8 MB.'))
        header = upload.read(12)
        upload.seek(0)
        if header.startswith(b'%PDF-'):
            if not upload.name.lower().endswith('.pdf'):
                raise forms.ValidationError(_('Use a PDF, JPG, PNG or WebP file.'))
            return upload
        try:
            image = Image.open(upload)
            image.verify()
            image_type = image.format
        except (UnidentifiedImageError, OSError, ValueError) as exc:
            raise forms.ValidationError(_('Use a PDF, JPG, PNG or WebP file.')) from exc
        finally:
            upload.seek(0)
        allowed = {'JPEG': '.jpg', 'PNG': '.png', 'WEBP': '.webp'}
        suffix = upload.name.lower().rsplit('.', 1)[-1]
        if image_type not in allowed or suffix not in {'jpg', 'jpeg', 'png', 'webp'}:
            raise forms.ValidationError(_('Use a PDF, JPG, PNG or WebP file.'))
        return upload

    def clean_screenshot(self):
        return self._check_upload('screenshot')

    def clean_passport(self):
        return self._check_upload('passport')


def flight_match(request):
    form = FlightMatchForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        # Do not silently accept requests if the notification channel is not configured.
        if not settings.EMAIL_HOST or not settings.EMAIL_HOST_USER:
            form.add_error(None, _('The request service is temporarily unavailable. Please contact us directly.'))
        else:
            match = form.save(commit=False)
            match.reference = f'SM-{uuid4().hex[:10].upper()}'
            match.notes = (
                'Preferred payment: ' + dict(form.fields['payment_preference'].choices)[form.cleaned_data['payment_preference']]
                + '\nTotal price visible in screenshot: confirmed'
            )
            match.save()
            admin_url = request.build_absolute_uri(
                reverse('admin:website_flightmatchrequest_change', args=[match.pk])
            )
            body = (
                f'New flight match request {match.reference}\n\n'
                f'Name: {match.full_name}\nEmail: {match.email or "—"}\nPhone: {match.phone or "—"}\n'
                f'Route: {match.route or "—"}\nTravel dates: {match.travel_dates or "—"}\n'
                f'Offer price: {match.offered_price or "—"} {match.offered_currency}\n'
                f'Passengers: {match.passengers}\nNotes: {match.notes or "—"}\n\n'
                f'Screenshot: attached in private admin record\nPassport: {"attached" if match.passport else "not provided"}\n'
                f'Open securely: {admin_url}\n'
            )
            try:
                sent = send_mail(
                    f'Sama Match request {match.reference}', body,
                    settings.DEFAULT_FROM_EMAIL, [settings.FLIGHT_MATCH_TO_EMAIL],
                    fail_silently=False,
                )
                if sent != 1:
                    raise RuntimeError('Email backend did not confirm delivery')
            except Exception:
                logger.exception('Flight match email failed for reference %s', match.reference)
                messages.error(request, _('Your request was saved, but email delivery failed. Please contact Sama Tours with your reference number: %(reference)s') % {'reference': match.reference})
                return redirect('website:flight_match')
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
