from django.contrib import admin
from .models import PasswordReset, Wallet, Transaction, UserToUserTransfer

admin.site.register(PasswordReset)
admin.site.register(Wallet)
admin.site.register(Transaction)
admin.site.register(UserToUserTransfer)

from .models import UserMessage

@admin.register(UserMessage)
class UserMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')
    search_fields = ('user__username', 'title')
