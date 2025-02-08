from django.db import models
from django.contrib.auth.models import User
import trading
import uuid

class TradingPair(models.Model):
    symbol = models.CharField(max_length=10, unique=True)
    base_currency = models.CharField(max_length=5)
    quote_currency = models.CharField(max_length=5)
    min_quantity = models.DecimalField(max_digits=18, decimal_places=8)
    
    def __str__(self):
        return self.symbol

class OrderModel(models.Model):
    ORDER_SIDE = (
        ('BUY', trading.Side.BUY.name),
        ('SELL', trading.Side.SELL.name),
    )
    ORDER_STATUS = (
        ('NEW', trading.OrderStatus.NEW.name),
        ('FILLED', trading.OrderStatus.FILLED.name),
        ('CANCELLED', trading.OrderStatus.CANCELLED.name),
        ('REJECTED', trading.OrderStatus.REJECTED.name),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    side = models.CharField(max_length=4, choices=ORDER_SIDE)
    quantity = models.DecimalField(max_digits=18, decimal_places=8)
    price = models.DecimalField(max_digits=18, decimal_places=8)
    status = models.CharField(max_length=10, choices=ORDER_STATUS, default='NEW')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def to_trading_order(self):
        price = trading.Price()
        price.value = float(self.price)
        
        # Create order with the correct side
        side = trading.Side.BUY if self.side == 'BUY' else trading.Side.SELL
        
        # Create order with proper symbol format
        symbol = self.trading_pair.symbol
        
        # Create the order using the correct constructor
        order = trading.Order(
            symbol,
            side,
            float(self.quantity),
            price
        )
        
        # Update status if needed
        if self.status != 'NEW':
            order.setStatus(getattr(trading.OrderStatus, self.status))
            
        return order
        
    def __str__(self):
        return f"{self.side} {self.quantity} {self.trading_pair.symbol} @ {self.price}"
    
class TradeModel(models.Model):
    buy_order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='buy_trades')
    sell_order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='sell_trades')
    trading_pair = models.ForeignKey(TradingPair, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=18, decimal_places=8)
    price = models.DecimalField(max_digits=18, decimal_places=8)
    timestamp = models.DateTimeField(auto_now_add=True)
    
class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balances')
    currency = models.CharField(max_length=5)  # USD, BTC, ETH, etc.
    amount = models.DecimalField(max_digits=30, decimal_places=8, default=0)
    
    class Meta:
        unique_together = ['user', 'currency']
        
    def __str__(self):
        return f"{self.user.username}: {self.amount} {self.currency}"