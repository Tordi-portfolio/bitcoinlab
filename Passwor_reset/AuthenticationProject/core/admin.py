from django.contrib import admin
from .models import PasswordReset, Wallet, Transaction

admin.site.register(PasswordReset)
admin.site.register(Wallet)
admin.site.register(Transaction)