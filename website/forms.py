from django import forms
from django.utils.translation import gettext_lazy as _


class EsimPurchaseForm(forms.Form):
    bundle_code = forms.CharField(max_length=220, widget=forms.HiddenInput())
    bundle_name = forms.CharField(max_length=300, required=False, widget=forms.HiddenInput())
    bundle_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.HiddenInput(),
    )
    customer_name = forms.CharField(
        max_length=120,
        label=_('Full name'),
        widget=forms.TextInput(attrs={'autocomplete': 'name', 'required': True}),
    )
    customer_email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'required': True}),
    )
    customer_whatsapp = forms.CharField(
        max_length=40,
        required=False,
        label=_('WhatsApp number'),
        widget=forms.TextInput(attrs={'autocomplete': 'tel', 'placeholder': '+961...'}),
    )
    confirm_live = forms.BooleanField(
        label=_('I understand this is a live purchase charged to the Sama Tours eSIM wallet.'),
        required=True,
    )


class EsimOrderLookupForm(forms.Form):
    order_reference = forms.CharField(
        max_length=30,
        label=_('Order reference'),
        widget=forms.TextInput(attrs={
            'autocomplete': 'off',
            'placeholder': 'SAM-…',
            'required': True,
        }),
    )
    customer_email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'autocomplete': 'email', 'required': True}),
    )
