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