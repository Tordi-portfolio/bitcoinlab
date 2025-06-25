# utils.py
from django.utils import timezone
from datetime import timedelta
from .models import Wallet
from decimal import Decimal

def apply_daily_bonus():
    now = timezone.now()
    wallets = Wallet.objects.all()

    for wallet in wallets:
        # Check if 24 hours has passed
        if now - wallet.last_bonus_added >= timedelta(hours=24):

            # Apply 5% to each balance
            wallet.bitcoin_balance += wallet.bitcoin_balance * Decimal('0.05')
            wallet.eth_balance += wallet.eth_balance * Decimal('0.05')
            wallet.usdt_balance += wallet.usdt_balance * Decimal('0.05')
            wallet.ton_balance += wallet.ton_balance * Decimal('0.05')
            wallet.solana_balance += wallet.solana_balance * Decimal('0.05')
            wallet.bnb_balance += wallet.bnb_balance * Decimal('0.05')
            wallet.tron_balance += wallet.tron_balance * Decimal('0.05')
            wallet.doge_balance += wallet.doge_balance * Decimal('0.05')
            wallet.sui_balance += wallet.sui_balance * Decimal('0.05')
            wallet.bgb_balance += wallet.bgb_balance * Decimal('0.05')

            wallet.last_bonus_added = now
            wallet.save()
