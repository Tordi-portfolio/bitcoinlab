from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Wallet  # change to your actual app name

class Command(BaseCommand):
    help = 'Adds 5% bonus to all wallet balances every 24 hours'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        for wallet in Wallet.objects.all():
            if (now - wallet.last_bonus_added) >= timedelta(hours=24):
                # Add 5% to all balances
                wallet.bitcoin_balance += wallet.bitcoin_balance * 0.05
                wallet.eth_balance += wallet.eth_balance * 0.05
                wallet.usdt_balance += wallet.usdt_balance * 0.05
                wallet.ton_balance += wallet.ton_balance * 0.05
                wallet.sol_balance += wallet.sol_balance * 0.05
                wallet.last_bonus_added = now
                wallet.save()
                self.stdout.write(f"✅ Bonus added for {wallet.user.username}")
            else:
                self.stdout.write(f"⏳ Not yet time for {wallet.user.username}")
