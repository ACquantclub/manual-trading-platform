from django.db import models
from django.contrib.auth.models import User
from trading import Market, Order, Side, Price
from decimal import Decimal

class TradingUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)

    def __str__(self):
        return f"{self.user.username} (Balance: ${self.balance})"

class OrderModel(models.Model):
    SIDE_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    
    user = models.ForeignKey(TradingUser, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='NEW')

    def to_trading_order(self):
        side = Side.BUY if self.side == 'BUY' else Side.SELL
        price = Price()
        price.value = float(self.price)
        return Order(self.symbol, side, float(self.quantity), price)

class TradeModel(models.Model):
    buy_order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='buy_trades')
    sell_order = models.ForeignKey(OrderModel, on_delete=models.CASCADE, related_name='sell_trades')
    symbol = models.CharField(max_length=10)
    quantity = models.DecimalField(max_digits=15, decimal_places=2)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)