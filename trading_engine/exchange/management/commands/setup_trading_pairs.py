from django.core.management.base import BaseCommand
from exchange.models import TradingPair
from exchange.trading_pairs import TRADING_PAIRS
from django.db import transaction

class Command(BaseCommand):
    help = 'Sets up the initial trading pairs for the platform'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Clear existing pairs
            TradingPair.objects.all().delete()
            
            # Create new pairs
            for pair_data in TRADING_PAIRS:
                TradingPair.objects.create(**pair_data)
                self.stdout.write(
                    self.style.SUCCESS(f'Created trading pair {pair_data["symbol"]}')
                )