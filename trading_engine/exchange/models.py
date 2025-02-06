from django.db import models
from django.contrib.auth.models import User
from trading import Order, Side, Price, Position
from decimal import Decimal
from django.db.models import Q
import logging

class TradingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    
    logger = logging.getLogger(__name__)
    
    def get_positions(self):
        """Get all positions for this user"""
        positions = []
        trades = TradeModel.objects.filter(
            Q(buy_order__user=self) | Q(sell_order__user=self)
        ).order_by('timestamp')
        
        position_map = {}
        for trade in trades:
            symbol = trade.symbol
            if symbol not in position_map:
                position_map[symbol] = Position(symbol)
                
            # Create Price object using __new__
            price = Price.__new__(Price)
            price.value = float(trade.price)
            quantity = float(trade.quantity)
            
            if trade.buy_order.user == self:
                # Note the changed order of parameters to match C++ signature
                order = Order(str(trade.id), Side.BUY, quantity, price)
            else:
                order = Order(str(trade.id), Side.SELL, quantity, price)
                
            position_map[symbol].updatePosition(order)
                    
        return position_map.values()

    def __str__(self):
        return f"{self.user.username} (Balance: ${self.balance})"

class OrderModel(models.Model):
    SIDE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    logger = logging.getLogger(__name__)  # Add logger at class level
    
    user = models.ForeignKey(TradingUser, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='NEW')

    def to_trading_order(self):
        """Convert database order to trading engine order"""
        try:
            # Create Price object using __new__
            price = Price.__new__(Price)
            price.value = float(self.price)
            
            # Convert side string to Side enum
            side = Side.BUY if self.side == 'BUY' else Side.SELL
            
            # Create Order with correct parameters matching C++ signature
            return Order(
                str(self.id),
                side,  # Side enum
                float(self.quantity),
                price
            )
        except Exception as e:
            self.logger.error(f"Failed to convert order to trading order: {e}")
            raise ValueError(f"Failed to create trading order: {str(e)}")

class TradeModel(models.Model):
    buy_order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='buy_trades')
    sell_order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='sell_trades')
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)