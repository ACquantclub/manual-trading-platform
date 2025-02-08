from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exchange.models import TradingPair, OrderModel
from exchange.market_manager import MarketManager
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Creates test orders for the trading platform'

    def handle(self, *args, **kwargs):
        market_manager = MarketManager()
        try:
            trading_pair = TradingPair.objects.get(symbol='AAPLUSD')
        except TradingPair.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('AAPLUSD trading pair not found. Run setup_trading_pairs first.')
            )
            return

        users = User.objects.all()[:2]
        
        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR('Need at least 2 users. Run create_test_users first.')
            )
            return

        # Create opposing orders
        test_orders = [
            {
                'user': users[0],
                'trading_pair': trading_pair,
                'side': 'BUY',
                'quantity': 0.1,
                'price': 45000
            },
            {
                'user': users[1],
                'trading_pair': trading_pair,
                'side': 'SELL',
                'quantity': 0.1,
                'price': 45000
            }
        ]

        with transaction.atomic():
            for order_data in test_orders:
                try:
                    order = OrderModel.objects.create(**order_data)
                    trades = market_manager.add_order(order)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created {order_data["side"]} order for {order_data["quantity"]} '
                            f'{order_data["trading_pair"].symbol} @ {order_data["price"]}'
                        )
                    )
                    if trades and len(trades) > 0:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Order matched! {len(trades)} trade(s) executed at price '
                                f'{trades[0].getPrice().value}'
                            )
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating order: {str(e)}')
                    )