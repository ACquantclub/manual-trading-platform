from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from exchange.models import TradingUser, OrderModel, TradeModel

class TestTradingUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.trading_user = TradingUser.objects.create(user=self.user, balance=Decimal('1000.00'))

    def test_trading_user_creation(self):
        self.assertEqual(self.trading_user.balance, Decimal('1000.00'))
        self.assertEqual(str(self.trading_user), "testuser (Balance: $1000.00)")

    def test_get_positions(self):
        # Create another user for trading
        user2 = User.objects.create_user(username='trader2', password='pass123')
        trading_user2 = TradingUser.objects.create(user=user2, balance=Decimal('1000.00'))
        
        # Create orders
        buy_order = OrderModel.objects.create(
            user=self.trading_user,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        sell_order = OrderModel.objects.create(
            user=trading_user2,
            symbol='AAPL',
            side='SELL',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        # Create trade
        TradeModel.objects.create(
            buy_order=buy_order,
            sell_order=sell_order,
            symbol='AAPL',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        positions = self.trading_user.get_positions()
        self.assertEqual(len(list(positions)), 1)