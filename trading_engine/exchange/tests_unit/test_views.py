from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from exchange.models import TradingUser, OrderModel
from unittest.mock import patch, Mock
import json

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.trading_user = TradingUser.objects.create(user=self.user, balance=Decimal('10000.00'))
        self.client.login(username='testuser', password='pass123')

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'exchange/dashboard.html')

    @patch('exchange.views.market_manager.submit_order')
    def test_submit_order_view(self, mock_submit_order):
        # Setup mock
        mock_order = OrderModel.objects.create(
            user=self.trading_user,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        mock_submit_order.return_value = (mock_order, [])

        data = {
            'symbol': 'AAPL',
            'side': 'BUY',
            'quantity': '10',
            'price': '150.00'
        }
        response = self.client.post(reverse('submit_order'), data)
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['order_id'], mock_order.id)

    def test_order_book_view(self):
        response = self.client.get(reverse('order_book', kwargs={'symbol': 'AAPL'}))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertIn('bids', data)
        self.assertIn('asks', data)

    def test_user_orders_view(self):
        # Create test order
        OrderModel.objects.create(
            user=self.trading_user,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00')
        )
        
        response = self.client.get(reverse('user_orders'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertEqual(len(data['orders']), 1)

    @patch('exchange.views.market_manager')
    def test_cancel_order_view(self, mock_market_manager):
        # Create test order
        order = OrderModel.objects.create(
            user=self.trading_user,
            symbol='AAPL',
            side='BUY',
            quantity=Decimal('10'),
            price=Decimal('150.00'),
            status='NEW'
        )
        
        # Create mock trading order
        mock_trading_order = Mock()
        
        # Mock the to_trading_order method on OrderModel
        with patch.object(OrderModel, 'to_trading_order') as mock_to_trading_order:
            mock_to_trading_order.return_value = mock_trading_order
            
            # Setup market manager mock
            mock_market = Mock()
            mock_market_manager.market = mock_market
            mock_market_manager.market.cancelOrder.return_value = None
            
            response = self.client.post(reverse('cancel_order', kwargs={'order_id': order.id}))
            self.assertEqual(response.status_code, 200)
            
            # Verify order was cancelled
            order.refresh_from_db()
            self.assertEqual(order.status, 'CANCELLED')
            
            # Verify mocks were called correctly
            mock_to_trading_order.assert_called_once()
            mock_market_manager.market.cancelOrder.assert_called_once_with(mock_trading_order)