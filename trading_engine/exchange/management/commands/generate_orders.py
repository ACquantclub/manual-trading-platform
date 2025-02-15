from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from exchange.models import TradingPair, OrderModel, Balance
from exchange.market_manager import MarketManager
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Creates test orders for the trading platform'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Trading pair symbol (e.g., BTCUSD)')
        parser.add_argument('--scenario', type=str, default='basic',
                          choices=['basic', 'spread', 'depth'],
                          help='Test scenario to generate')

    def handle(self, *args, **kwargs):
        symbol = kwargs['symbol'].upper()
        scenario = kwargs['scenario']
        
        market_manager = MarketManager()
        try:
            trading_pair = TradingPair.objects.get(symbol=symbol)
        except TradingPair.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'{symbol} trading pair not found. Run setup_trading_pairs first.')
            )
            return

        users = list(User.objects.filter(username__startswith='trader'))
        
        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR('Need at least 2 users. Run create_users first.')
            )
            return

        scenarios = {
            'basic': self._basic_scenario,
            'spread': self._spread_scenario,
            'depth': self._depth_scenario
        }

        scenario_func = scenarios.get(scenario)
        if scenario_func:
            scenario_func(trading_pair, users, market_manager)

    def _basic_scenario(self, trading_pair, users, market_manager):
        """Creates a simple matching buy and sell order"""
        base_price = 45000 if trading_pair.symbol.startswith('BTC') else 180
        
        test_orders = [
            {
                'user': users[0],
                'trading_pair': trading_pair,
                'side': 'BUY',
                'quantity': 1.0,
                'price': base_price
            },
            {
                'user': users[1],
                'trading_pair': trading_pair,
                'side': 'SELL',
                'quantity': 1.0,
                'price': base_price
            }
        ]
        self._create_orders(test_orders, market_manager)

    def _spread_scenario(self, trading_pair, users, market_manager):
        """Creates orders with a price spread"""
        base_price = 45000 if trading_pair.symbol.startswith('BTC') else 180
        
        test_orders = [
            {
                'user': users[0],
                'trading_pair': trading_pair,
                'side': 'BUY',
                'quantity': 1.0,
                'price': base_price * 0.99  # 1% below
            },
            {
                'user': users[1],
                'trading_pair': trading_pair,
                'side': 'SELL',
                'quantity': 1.0,
                'price': base_price * 1.01  # 1% above
            }
        ]
        self._create_orders(test_orders, market_manager)

    def _depth_scenario(self, trading_pair, users, market_manager):
        """Creates multiple orders at different price levels"""
        base_price = 45000 if trading_pair.symbol.startswith('BTC') else 180
        test_orders = []

        # Create buy orders
        for i in range(5):
            test_orders.append({
                'user': users[0],
                'trading_pair': trading_pair,
                'side': 'BUY',
                'quantity': 1.0,
                'price': base_price * (1 - i * 0.01)  # Steps down by 1%
            })

        # Create sell orders
        for i in range(5):
            test_orders.append({
                'user': users[1],
                'trading_pair': trading_pair,
                'side': 'SELL',
                'quantity': 1.0,
                'price': base_price * (1 + i * 0.01)  # Steps up by 1%
            })
        
        self._create_orders(test_orders, market_manager)
        
    def _create_orders(self, test_orders, market_manager):
        """Create and process orders with proper transaction handling"""
        for order_data in test_orders:
            try:
                with transaction.atomic():
                    # Ensure user has required balances
                    if order_data['side'] == 'BUY':
                        required_balance = order_data['price'] * order_data['quantity']
                        currency = order_data['trading_pair'].quote_currency
                    else:
                        required_balance = order_data['quantity']
                        currency = order_data['trading_pair'].base_currency

                    # Get or create balance
                    balance, created = Balance.objects.get_or_create(
                        user=order_data['user'],
                        currency=currency,
                        defaults={'amount': 1000000.0}  # Initial balance of 1M
                    )

                    # Create complementary balance if needed
                    complementary_currency = (
                        order_data['trading_pair'].base_currency 
                        if order_data['side'] == 'BUY' 
                        else order_data['trading_pair'].quote_currency
                    )
                    Balance.objects.get_or_create(
                        user=order_data['user'],
                        currency=complementary_currency,
                        defaults={'amount': 1000000.0}
                    )

                    # Create and save the order
                    order = OrderModel.objects.create(
                        user=order_data['user'],
                        trading_pair=order_data['trading_pair'],
                        side=order_data['side'],
                        quantity=order_data['quantity'],
                        price=order_data['price'],
                        status='NEW'
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Created {order_data["side"]} order for {order_data["quantity"]} '
                            f'{order_data["trading_pair"].symbol} @ {order_data["price"]}'
                        )
                    )

                # Process order matching outside the transaction
                trades = market_manager.add_order(order)
                
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