from django.db import models
from django.contrib.auth.models import User
import uuid
from decimal import Decimal
from django.utils import timezone

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bitcoin_balance = models.DecimalField(max_digits=20, decimal_places=10, default=Decimal('0.0000000000'))
    eth_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    usdt_balance = models.DecimalField(max_digits=14, decimal_places=5, default=Decimal('0.00000'))
    ton_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    solana_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    bnb_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    tron_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    doge_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    sui_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    bgb_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))
    usdc_balance = models.DecimalField(max_digits=12, decimal_places=5, default=Decimal('0.00000'))

    last_bonus_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [('deposit', 'Deposit'), ('withdrawal', 'Withdrawal')]
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed'), ('reversed', 'Reversed')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    address = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now) 


class DepositConfirmation(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'USDT (Tether)'),
        ('BNB', 'BNB'),
        ('TON', 'TON'),
        ('SOL', 'SOL'),
        ('USDC', 'USDC'),
        ('SUI', 'SUI'),
        ('DOGE', 'DOGE'),
        ('BGB', 'BGB'),
        ('TRON', 'TRON'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    crypto = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    receipt = models.FileField(upload_to='deposit_receipts/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.crypto} - {self.amount}"
    

class UserToUserTransfer(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        ('USDT', 'USDT'),
        ('TON', 'Toncoin'),
        ('SOL', 'Solana'),
        ('BNB', 'binancecoin'),

        ('USDC', 'USDC'),
        ('SUI', 'SUI'),
        ('DOGE', 'DOGE'),
        ('BGB', 'BGB'),
        ('TRON', 'TRON'),
    ]

    sender = models.ForeignKey(User, related_name='sent_transfers', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_transfers', on_delete=models.CASCADE)
    crypto = models.CharField(max_length=10, choices=CRYPTO_CHOICES)
    amount = models.DecimalField(max_digits=18, decimal_places=8)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('completed', 'Completed')], default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} sent {self.amount} {self.crypto} to {self.recipient.username}"
    

from django.db import models
from django.contrib.auth.models import User

class UserMessage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_message')
    title = models.CharField(max_length=100, blank=True)
    message = models.TextField(default='0')

    def __str__(self):
        return f"Message for {self.user.username}"
