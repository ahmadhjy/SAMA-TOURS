import json
from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from .ims_countries import iso3_countries


class InsuranceQuoteForm(forms.Form):
    residence_country = forms.ChoiceField(
        label=_('Country of residence'),
        choices=[],
        initial='LBN',
    )
    destination_country = forms.ChoiceField(
        label=_('Destination'),
        choices=[],
    )
    from_date = forms.DateField(
        label=_('Departure date'),
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
    )
    till_date = forms.DateField(
        label=_('Return date'),
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
    )
    traveller_count = forms.IntegerField(
        label=_('Number of travellers'),
        min_value=1,
        max_value=6,
        initial=1,
        widget=forms.NumberInput(attrs={'min': 1, 'max': 6}),
    )
    birth_date_1 = forms.DateField(
        label=_('Traveller 1 — date of birth'),
        widget=forms.DateInput(attrs={'type': 'date', 'required': True}),
    )
    birth_date_2 = forms.DateField(
        label=_('Traveller 2 — date of birth'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    birth_date_3 = forms.DateField(
        label=_('Traveller 3 — date of birth'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    birth_date_4 = forms.DateField(
        label=_('Traveller 4 — date of birth'),
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        country_choices = [('', _('Select country'))] + iso3_countries()
        self.fields['residence_country'].choices = country_choices
        self.fields['destination_country'].choices = country_choices
        today = date.today().isoformat()
        self.fields['from_date'].widget.attrs['min'] = today
        self.fields['till_date'].widget.attrs['min'] = today

    def clean(self):
        cleaned = super().clean()
        from_date = cleaned.get('from_date')
        till_date = cleaned.get('till_date')
        if from_date and till_date and till_date < from_date:
            raise forms.ValidationError(_('Return date must be on or after departure date.'))
        if from_date and from_date < date.today():
            raise forms.ValidationError(_('Departure date cannot be in the past.'))

        count = cleaned.get('traveller_count') or 1
        for idx in range(2, count + 1):
            field = self.fields.get(f'birth_date_{idx}')
            if field and not cleaned.get(f'birth_date_{idx}'):
                self.add_error(f'birth_date_{idx}', _('Date of birth is required for each traveller.'))
        return cleaned

    def traveller_birth_dates(self) -> list[str]:
        count = self.cleaned_data.get('traveller_count') or 1
        dates = []
        for idx in range(1, count + 1):
            value = self.cleaned_data.get(f'birth_date_{idx}')
            if value:
                dates.append(value.isoformat())
        return dates

    def destinations_payload(self) -> list[dict[str, str]]:
        return [{
            'country': self.cleaned_data['destination_country'],
            'from_date': self.cleaned_data['from_date'].isoformat(),
            'till_date': self.cleaned_data['till_date'].isoformat(),
        }]

    def quote_session_data(self) -> dict:
        return {
            'residence_country': self.cleaned_data['residence_country'],
            'destination_country': self.cleaned_data['destination_country'],
            'from_date': self.cleaned_data['from_date'].isoformat(),
            'till_date': self.cleaned_data['till_date'].isoformat(),
            'traveller_count': self.cleaned_data['traveller_count'],
            'birth_dates': self.traveller_birth_dates(),
        }


class InsurancePurchaseForm(forms.Form):
    plan_id = forms.IntegerField(widget=forms.HiddenInput())
    plan_name = forms.CharField(max_length=200, widget=forms.HiddenInput())
    plan_price = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.HiddenInput())
    plan_currency = forms.CharField(max_length=8, initial='USD', widget=forms.HiddenInput())
    deductible_tier = forms.ChoiceField(
        choices=[('0', _('No deductible')), ('1', _('With deductible'))],
        widget=forms.RadioSelect,
        initial='0',
    )
    quote_data = forms.CharField(widget=forms.HiddenInput())
    price_ids = forms.CharField(widget=forms.HiddenInput())

    email = forms.EmailField(label=_('Email'))
    phone = forms.CharField(max_length=40, label=_('Phone'))
    address = forms.CharField(max_length=300, label=_('Address'))

    traveller_1_gender = forms.ChoiceField(
        choices=[('M', _('Male')), ('F', _('Female'))],
        label=_('Traveller 1 — gender'),
    )
    traveller_1_first_name = forms.CharField(max_length=80, label=_('Traveller 1 — first name'))
    traveller_1_last_name = forms.CharField(max_length=80, label=_('Traveller 1 — last name'))
    traveller_1_passport = forms.CharField(max_length=40, required=False, label=_('Traveller 1 — passport'))
    traveller_1_passport_expiry = forms.DateField(
        required=False,
        label=_('Traveller 1 — passport expiry'),
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    traveller_2_gender = forms.ChoiceField(
        choices=[('M', _('Male')), ('F', _('Female'))],
        required=False,
        label=_('Traveller 2 — gender'),
    )
    traveller_2_first_name = forms.CharField(max_length=80, required=False, label=_('Traveller 2 — first name'))
    traveller_2_last_name = forms.CharField(max_length=80, required=False, label=_('Traveller 2 — last name'))
    traveller_2_passport = forms.CharField(max_length=40, required=False, label=_('Traveller 2 — passport'))
    traveller_2_passport_expiry = forms.DateField(
        required=False,
        label=_('Traveller 2 — passport expiry'),
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    traveller_3_gender = forms.ChoiceField(
        choices=[('M', _('Male')), ('F', _('Female'))],
        required=False,
        label=_('Traveller 3 — gender'),
    )
    traveller_3_first_name = forms.CharField(max_length=80, required=False, label=_('Traveller 3 — first name'))
    traveller_3_last_name = forms.CharField(max_length=80, required=False, label=_('Traveller 3 — last name'))

    traveller_4_gender = forms.ChoiceField(
        choices=[('M', _('Male')), ('F', _('Female'))],
        required=False,
        label=_('Traveller 4 — gender'),
    )
    traveller_4_first_name = forms.CharField(max_length=80, required=False, label=_('Traveller 4 — first name'))
    traveller_4_last_name = forms.CharField(max_length=80, required=False, label=_('Traveller 4 — last name'))

    confirm_sandbox = forms.BooleanField(
        required=False,
        label=_('I understand this is a sandbox test policy (no payment).'),
    )
    confirm_terms = forms.BooleanField(
        required=True,
        label=_('I agree to proceed with travel insurance issuance.'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_class = 'insurance-purchase-input'
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.DateInput)):
                widget.attrs.setdefault('class', input_class)
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault('class', input_class)

        self.fields['email'].widget.attrs.setdefault('placeholder', 'you@example.com')
        self.fields['email'].widget.attrs.setdefault('autocomplete', 'email')
        self.fields['phone'].widget.attrs.setdefault('placeholder', '+961 …')
        self.fields['phone'].widget.attrs.setdefault('autocomplete', 'tel')
        self.fields['address'].widget = forms.Textarea(attrs={
            'class': input_class,
            'rows': 2,
            'placeholder': _('Street, city, country'),
        })
        self.fields['traveller_1_first_name'].widget.attrs.setdefault('placeholder', _('First name'))
        self.fields['traveller_1_last_name'].widget.attrs.setdefault('placeholder', _('Last name'))
        self.fields['traveller_1_passport'].widget.attrs.setdefault('placeholder', _('Passport number'))

    def clean_quote_data(self):
        raw = self.cleaned_data.get('quote_data') or '{}'
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise forms.ValidationError(_('Quote expired — please search again.')) from exc
        if not data.get('birth_dates'):
            raise forms.ValidationError(_('Quote expired — please search again.'))
        return data

    def clean_price_ids(self):
        raw = (self.cleaned_data.get('price_ids') or '').strip()
        if not raw:
            raise forms.ValidationError(_('Please select a plan again.'))
        try:
            return [int(part) for part in raw.split(',') if part]
        except ValueError as exc:
            raise forms.ValidationError(_('Invalid plan selection.')) from exc

    def travellers_payload(self, quote_data: dict, price_ids: list[int]) -> list[dict]:
        travellers = []
        birth_dates = quote_data.get('birth_dates') or []
        residence = quote_data.get('residence_country') or 'LBN'
        for idx, birth_date in enumerate(birth_dates):
            n = idx + 1
            first = self.cleaned_data.get(f'traveller_{n}_first_name')
            last = self.cleaned_data.get(f'traveller_{n}_last_name')
            gender = self.cleaned_data.get(f'traveller_{n}_gender')
            if not first or not last:
                continue
            row: dict = {
                'gender': gender or 'M',
                'first_name': first,
                'middle_name': '',
                'maiden_name': '',
                'last_name': last,
                'birth_date': birth_date,
                'nationality': residence,
            }
            passport = self.cleaned_data.get(f'traveller_{n}_passport')
            passport_exp = self.cleaned_data.get(f'traveller_{n}_passport_expiry')
            if passport:
                row['passport'] = passport
            if passport_exp:
                row['passport_expiry'] = passport_exp.isoformat()
            if idx < len(price_ids):
                row['plan_price_id'] = price_ids[idx]
            travellers.append(row)
        return travellers


class InsuranceLookupForm(forms.Form):
    order_reference = forms.CharField(
        max_length=30,
        label=_('Policy reference'),
        widget=forms.TextInput(attrs={
            'placeholder': 'SAM-INS-XXXXXXXXXX',
            'autocomplete': 'off',
            'class': 'insurance-lookup-input',
            'inputmode': 'text',
            'spellcheck': 'false',
        }),
    )
    customer_email = forms.EmailField(
        label=_('Email used at purchase'),
        widget=forms.EmailInput(attrs={
            'placeholder': 'you@example.com',
            'autocomplete': 'email',
            'class': 'insurance-lookup-input',
        }),
    )
