from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bitcoin_balance = models.DecimalField(max_digits=16, decimal_places=10, default=0.00000000)
    eth_balance = models.DecimalField(max_digits=16, decimal_places=10, default=0.0000)
    usdt_balance = models.DecimalField(max_digits=16, decimal_places=10, default=0.0000)
    ton_balance = models.DecimalField(max_digits=16, decimal_places=10, default=0.000)
    solana_balance = models.DecimalField(max_digits=16, decimal_places=10, default=0.000)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class DepositConfirmation(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'USDT (Tether)'),
        ('BNB', 'BNB'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    crypto = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    receipt = models.FileField(upload_to='deposit_receipts/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.crypto} - {self.amount}"