from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm

class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Old Password'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm New Password'}))



from django import forms
from .models import Profile

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']

