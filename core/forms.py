from django import forms
from .models import Transaction, DepositConfirmation


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'status', 'user', 'amount', 'address']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),  # This uses the choices from the model
            'user': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if not self.instance.pk:
                self.fields['status'].initial = 'pending'



class DepositConfirmationForm(forms.ModelForm):
    class Meta:
        model = DepositConfirmation
        fields = ['email', 'crypto', 'amount', 'receipt']



from django.contrib.auth.models import User
from .models import UserToUserTransfer

class UserToUserTransferForm(forms.Form):
    recipient_identifier = forms.CharField(
        label="Recipient Username or Email",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    crypto = forms.ChoiceField(
        choices=UserToUserTransfer.CRYPTO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    amount = forms.DecimalField(
        max_digits=18,
        decimal_places=8,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.00000001'})
    )

    def clean_recipient_identifier(self):
        identifier = self.cleaned_data['recipient_identifier']
        try:
            return User.objects.get(username=identifier)
        except User.DoesNotExist:
            try:
                return User.objects.get(email=identifier)
            except User.DoesNotExist:
                raise forms.ValidationError("Recipient not found using username or email.")
