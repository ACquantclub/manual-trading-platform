from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from exchange.models import TradingUser, OrderModel
from exchange.market_manager import MarketManager

class TestMarketManager(TestCase):
    def setUp(self):
        # Reset the singleton instance before each test
        MarketManager.reset_instance()
        
        # Create test users
        self.user1 = User.objects.create_user(username='trader1', password='pass123')
        self.user2 = User.objects.create_user(username='trader2', password='pass123')
        
        self.trading_user1 = TradingUser.objects.create(user=self.user1, balance=Decimal('10000.00'))
        self.trading_user2 = TradingUser.objects.create(user=self.user2, balance=Decimal('10000.00'))
        
        # Get fresh market manager instance
        self.market_manager = MarketManager()
        
        # Initialize order book
        self.symbol = 'AAPL'
        try:
            # Ensure clean state
            if self.market_manager.market.hasOrderBook(self.symbol):
                order_book = self.market_manager.market.getOrderBook(self.symbol)
                for order in order_book.getOrders():
                    self.market_manager.market.cancelOrder(order.getId())
            
            # Initialize order book
            self.market_manager._ensure_order_book_exists(self.symbol)
            
            if not self.market_manager.market.hasOrderBook(self.symbol):
                raise RuntimeError(f"Order book verification failed for {self.symbol}")
                
        except Exception as e:
            print(f"Order book initialization failed: {e}")
            raise

    def tearDown(self):
        try:
            # Clean up orders first
            if hasattr(self, 'market_manager') and hasattr(self.market_manager, 'market'):
                if self.market_manager.market.hasOrderBook(self.symbol):
                    order_book = self.market_manager.market.getOrderBook(self.symbol)
                    for order in order_book.getOrders():
                        try:
                            self.market_manager.market.cancelOrder(order.getId())
                        except Exception:
                            pass
        finally:
            # Reset the singleton instance
            MarketManager.reset_instance()

    def test_submit_order_success(self):
        order, trades = self.market_manager.submit_order(
            user=self.trading_user1,
            symbol=self.symbol,
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        self.assertEqual(order.status, 'NEW')
        self.assertEqual(order.symbol, self.symbol)
        self.assertEqual(order.quantity, Decimal('10'))
        self.assertEqual(len(trades), 0)

    def test_insufficient_balance(self):
        # First ensure order book exists
        self.market_manager._ensure_order_book_exists('AAPL')
        
        with self.assertRaises(ValueError):
            self.market_manager.submit_order(
                user=self.trading_user1,
                symbol='AAPL',
                side='BUY',
                quantity=Decimal('1000'),
                price=Decimal('1000.00')
            )

    def test_order_matching(self):
        # First ensure order book exists
        self.market_manager._ensure_order_book_exists('AAPL')
        
        # Submit buy order
        buy_order, _ = self.market_manager.submit_order(
            user=self.trading_user1,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        # Submit matching sell order
        sell_order, trades = self.market_manager.submit_order(
            user=self.trading_user2,
            symbol='AAPL',
            side='SELL',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].quantity, Decimal('10'))
        self.assertEqual(trades[0].price, Decimal('150.00'))

    def test_order_book(self):
        # First ensure order book exists
        self.market_manager._ensure_order_book_exists('AAPL')
        
        self.market_manager.submit_order(
            user=self.trading_user1,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        order_book = self.market_manager.get_order_book('AAPL')
        self.assertIsNotNone(order_book)
        
        orders = order_book.getOrders()
        self.assertTrue(len(orders) >= 1)  # At least one order should be present

    def test_market_summary(self):
        # First ensure order book exists
        self.market_manager._ensure_order_book_exists('AAPL')
        
        # Submit a test order
        self.market_manager.submit_order(
            user=self.trading_user1,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        summary = self.market_manager.get_market_summary('AAPL')
        self.assertIsNotNone(summary)
        self.assertEqual(summary['symbol'], 'AAPL')
        self.assertEqual(float(summary['bid']), 150.00)
        self.assertEqual(float(summary['buy_depth']), 10.0)