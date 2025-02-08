from trading import Market, OrderStatus, Side, Price, Order
from threading import Lock
from .models import OrderModel, TradeModel, TradingPair
import logging

logger = logging.getLogger(__name__)

class MarketManager:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.market = Market()
                cls._instance.order_map = {}
            return cls._instance

    def add_order(self, order_model):
        trading_order = order_model.to_trading_order()
        symbol = order_model.trading_pair.symbol
            
        try:
            # Ensure orderbook exists
            self.ensure_orderbook(symbol)
            
            logger.info(f"Adding order {order_model.order_id} to market")
            self.market.addOrder(trading_order)
            
            # Match orders and get trades
            trades = self.market.matchOrders(symbol)
            
            if trades:
                logger.info(f"Order {order_model.order_id} matched with {len(trades)} trades")
                for trade in trades:
                    buy_order_id = str(trade.getBuyOrderId())
                    sell_order_id = str(trade.getSellOrderId())
                    
                    try:
                        buy_order = OrderModel.objects.get(order_id=buy_order_id)
                        sell_order = OrderModel.objects.get(order_id=sell_order_id)
                        
                        # Update order statuses using C++ enum
                        buy_order.status = trading.OrderStatus.FILLED.name
                        sell_order.status = trading.OrderStatus.FILLED.name
                        buy_order.save()
                        sell_order.save()
                        
                        # Create trade record
                        TradeModel.objects.create(
                            buy_order=buy_order,
                            sell_order=sell_order,
                            trading_pair=order_model.trading_pair,
                            quantity=trade.getQuantity(),
                            price=trade.getPrice().value
                        )
                    except OrderModel.DoesNotExist as e:
                        logger.error(f"Order not found: buy={buy_order_id}, sell={sell_order_id}")
                        continue
                
                return trades
            
        except Exception as e:
            logger.error(f"Error adding order {order_model.order_id}: {str(e)}", exc_info=True)
            order_model.status = trading.OrderStatus.REJECTED.name
            order_model.save()
            raise RuntimeError(f"Failed to process order: {str(e)}")
            
    def ensure_orderbook(self, symbol):
        """Ensures an orderbook exists for the given symbol"""
        if not self.market.hasOrderBook(symbol):
            # Create a dummy order with valid quantity and price
            price = Price()
            price.value = 1.0  # Use 1.0 instead of 0.0
            dummy_order = Order(symbol, Side.BUY, 0.00000001, price)  # Use minimum valid quantity
            self.market.addOrder(dummy_order)
            self.market.cancelOrder(dummy_order.getId())