from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exchange.models import Balance
from exchange.trading_pairs import TRADING_PAIRS
from django.db import transaction

class Command(BaseCommand):
    help = 'Sets up initial test balances for users'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            # Get test users
            users = User.objects.filter(username__startswith='trader')
            
            if not users:
                self.stdout.write(
                    self.style.ERROR('No test users found. Run create_users first.')
                )
                return

            # Clear existing balances for test users
            Balance.objects.filter(user__in=users).delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing balances'))

            # Extract unique currencies from trading pairs
            currencies = {'USD'}  # Always include USD as quote currency
            for pair in TRADING_PAIRS:
                currencies.add(pair['base_currency'])

            # Set up initial balances for each user
            initial_amounts = {
                'USD': 10000000.0,  # $10M USD
                'AAPL': 1000.0,
                'MSFT': 1000.0,
                'GOOGL': 1000.0,
                'AMZN': 1000.0,
                'NVDA': 1000.0,
                'META': 1000.0,
                'TSLA': 1000.0,
                'JPM': 1000.0,
                'VIS': 1000.0,
                'KO': 1000.0,
                'WMT': 1000.0,
                'DIS': 1000.0
            }

            for user in users:
                for currency in currencies:
                    amount = initial_amounts.get(currency, 1000.0)  # Default 1000 units for any new currency
                    balance = Balance.objects.create(
                        user=user,
                        currency=currency,
                        amount=amount
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created balance for {user.username}: {amount} {currency}'
                        )
                    )