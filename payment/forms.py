from django import forms
from .models import CreditCard
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from datetime import datetime

class CreditCardForm(forms.ModelForm):

    cvc = forms.CharField(
        max_length=4,
        validators=[
            RegexValidator(r'^\d{3,4}$', message="CVC must contain 3 or 4 digits.")
        ],
        widget=forms.PasswordInput(render_value=True),
        help_text="Enter the CVC (3 or 4 digits)."
    )

    class Meta:
        model = CreditCard
        exclude = []

    def clean_card_number(self):
        card_number = self.cleaned_data.get('card_number')

        if not card_number:
            raise ValidationError("Card number is required.")
        
        # Remove spaces and hyphens
        normalized = card_number.replace(" ", "").replace("-", "")

        if not normalized.isdigit():
            raise ValidationError("Card number must contain only digits.")
        
        if len(normalized) < 13 or len(normalized) > 19:
            raise ValidationError("Card number must be between 13 and 19 digits.")
        
        return normalized



    def clean_exp_month(self):
        month = self.cleaned_data.get('exp_month')

        if not 1 <= month <= 12:
            raise ValidationError("Expiration month must be between 1 and 12.")
        
        return month

    def clean_exp_year(self):
        year = self.cleaned_data.get('exp_year')

        if year < datetime.now().year - 1:
            raise ValidationError("Expiration year cannot be in the past.")
        
        return year

    def clean_cvc(self):
        cvc = self.cleaned_data.get('cvc')

        if not cvc.isdigit():
            raise ValidationError("CVC must be numeric.")
        
        if len(cvc) not in (3, 4):
            raise ValidationError("CVC must be 3 or 4 digits.")
        
        return cvc

    def save(self, commit=True):
        # Remove the CVC from the saved model (if not stored)
        self.cleaned_data.pop('cvc', None)
        return super().save(commit=commit)

    def clean(self):
        cleaned_data = super().clean()
        exp_month = cleaned_data.get("exp_month")
        exp_year = cleaned_data.get("exp_year")

        if exp_month and exp_year:
            now = datetime.now()
            current_year = now.year
            current_month = now.month

            if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
                raise ValidationError("The expiration date must be in the future.")

        return cleaned_data

