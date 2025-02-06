from trading import Market, Side, OrderStatus, Price, Trade
from .models import OrderModel, TradeModel, TradingUser
from decimal import Decimal
from django.db import transaction
from typing import List, Optional
import logging
from trading import Market, Side, OrderStatus, Price, Trade, Order, OrderBook

logger = logging.getLogger(__name__)

class MarketManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketManager, cls).__new__(cls)
            cls._instance.market = Market()
            cls._instance._initialize()
        return cls._instance
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance - used for testing"""
        if cls._instance is not None:
            # Clear all order books first to prevent invalid memory access
            if hasattr(cls._instance, 'market'):
                # Get all symbols and cancel their orders
                for symbol in ['AAPL']:  # Add more symbols if needed
                    try:
                        if cls._instance.market.hasOrderBook(symbol):
                            order_book = cls._instance.market.getOrderBook(symbol)
                            for order in order_book.getOrders():
                                cls._instance.market.cancelOrder(order.getId())
                    except Exception:
                        pass
            
            # Now create a new Market instance
            cls._instance = None
    
    def _initialize(self):
        """Restore market state from database on startup"""
        try:
            active_orders = OrderModel.objects.filter(status='NEW')
            for order in active_orders:
                trading_order = order.to_trading_order()
                self.market.addOrder(trading_order)
        except Exception as e:
            logger.error(f"Failed to initialize market: {e}")
            
    def _ensure_order_book_exists(self, symbol: str) -> None:
        """Ensure order book exists for symbol"""
        if not self.market.hasOrderBook(symbol):
            try:
                # Create and keep reference to order book
                order_book = OrderBook(symbol)
                self.market.addOrderBook(order_book)
                
                # Create Price object
                price = Price()
                price.value = 1.0
                
                # Create dummy order
                dummy_order = Order(
                    f"{symbol}_init",
                    Side.BUY,
                    0.0001,
                    price
                )
                
                # Add and verify
                self.market.addOrder(dummy_order)
                if not self.market.hasOrderBook(symbol):
                    raise RuntimeError(f"Failed to create order book for {symbol}")
                    
                # Cleanup
                self.market.cancelOrder(dummy_order.getId())
                logger.info(f"Successfully initialized order book for {symbol}")
                
            except Exception as e:
                logger.error(f"Failed to initialize order book for {symbol}: {e}")
                raise

    @transaction.atomic
    def submit_order(self, user: TradingUser, symbol: str, side: str, 
                    quantity: Decimal, price: Decimal) -> tuple[OrderModel, List[TradeModel]]:
        """Submit and process a new order with transaction safety"""
        try:
            # Validate order parameters
            self._validate_order(user, symbol, side, quantity, price)

            # Ensure order book exists BEFORE any other operations
            self._ensure_order_book_exists(symbol)

            # Create and save order
            order = OrderModel.objects.create(
                user=user,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price,
                status='NEW'
            )

            # Convert price to trading engine format using __new__
            trading_price = Price.__new__(Price)
            trading_price.value = float(price)

            # Convert side string to enum
            trading_side = Side.BUY if side == 'BUY' else Side.SELL

            # Create trading order with correct types
            trading_order = Order(
                str(order.id),  # Convert ID to string
                trading_side,
                float(quantity),  # Convert to float for C++ binding
                trading_price
            )
            
            self.market.addOrder(trading_order)

            # Now match orders
            trades = []
            matched_trades = self._match_orders(symbol)
                
            for trade in matched_trades:
                trade_model = TradeModel.objects.create(
                    buy_order=OrderModel.objects.get(id=trade.getBuyOrderId()),
                    sell_order=OrderModel.objects.get(id=trade.getSellOrderId()),
                    symbol=symbol,
                    quantity=Decimal(str(trade.getQuantity())),
                    price=Decimal(str(trade.getPrice().value))
                )
                trades.append(trade_model)
                self._process_trade_settlement(trade_model)

            return order, trades

        except Exception as e:
            logger.error(f"Order submission failed: {e}")
            raise

    def _update_order_status(self, order: OrderModel, trading_order) -> None:
        """Update order status based on trading engine state"""
        status = trading_order.getStatus()
        if status == OrderStatus.FILLED:
            order.status = 'FILLED'
        elif status == OrderStatus.CANCELLED:
            order.status = 'CANCELLED'
        elif status == OrderStatus.REJECTED:
            order.status = 'REJECTED'
        order.save()

    @transaction.atomic
    def _process_trade_settlement(self, trade: TradeModel) -> None:
        """Handle the financial settlement of a trade"""
        trade_value = trade.quantity * trade.price
        
        # Update buyer's balance
        buyer = trade.buy_order.user
        buyer.balance -= trade_value
        buyer.save()
        
        # Update seller's balance
        seller = trade.sell_order.user
        seller.balance += trade_value
        seller.save()

    def get_order_book(self, symbol: str):
        """Get the current order book for a symbol"""
        try:
            self._ensure_order_book_exists(symbol)
            return self.market.getOrderBook(symbol)
        except Exception as e:
            logger.error(f"Failed to fetch order book: {e}")
            return None

    def get_position(self, symbol: str):
        """Get the current position for a symbol"""
        return self.market.getPosition(symbol)
    
    def _match_orders(self, symbol: str) -> List[Trade]:
        """Enhanced order matching with price-time priority"""
        order_book = self.market.getOrderBook(symbol)
        if not order_book:
            return []
            
        trades = self.market.matchOrders(symbol)
        
        # Handle partial fills
        for trade in trades:
            buy_order = OrderModel.objects.get(id=trade.getBuyOrderId())
            sell_order = OrderModel.objects.get(id=trade.getSellOrderId())
            
            # Update remaining quantities
            buy_remaining = float(buy_order.quantity) - trade.getQuantity()
            sell_remaining = float(sell_order.quantity) - trade.getQuantity()
            
            if buy_remaining > 0:
                self._create_remainder_order(buy_order, buy_remaining)
            if sell_remaining > 0:
                self._create_remainder_order(sell_order, sell_remaining)
                
        return trades

    def _create_remainder_order(self, original_order: OrderModel, remaining_quantity: float):
        """Create a new order for remaining quantity after partial fill"""
        OrderModel.objects.create(
            user=original_order.user,
            symbol=original_order.symbol,
            side=original_order.side,
            quantity=Decimal(str(remaining_quantity)),
            price=original_order.price,
            status='NEW'
        )
        
    def _validate_order(self, user: TradingUser, symbol: str, side: str, 
                    quantity: Decimal, price: Decimal) -> None:
        """Validate order before submission"""
        # Single max order size check
        max_order_size = Decimal('1000000')
        order_value = quantity * price
        
        if order_value > max_order_size:
            raise ValueError("Order size exceeds maximum allowed")
        
        # Position limits
        max_position = Decimal('1000000')
        
        try:
            current_position = self.get_position_value(user, symbol)
        except ValueError:
            current_position = Decimal('0')
            
        if current_position + order_value > max_position:
            raise ValueError("Position limit exceeded")

        # Price boundaries (prevent fat finger errors)
        last_trade = TradeModel.objects.filter(symbol=symbol).order_by('-timestamp').first()
        if last_trade:
            price_change = abs(price - last_trade.price) / last_trade.price
            if price_change > Decimal('0.1'):  # 10% price change limit
                raise ValueError("Price outside allowed range")

        # Validate sufficient balance for buy orders
        if side == 'BUY':
            required_balance = quantity * price
            if user.balance < required_balance:
                raise ValueError("Insufficient balance")

    def get_position_value(self, user: TradingUser, symbol: str) -> Decimal:
        """Calculate total position value for a user in a symbol"""
        position = self.market.getPosition(symbol)
        if position:
            return Decimal(str(abs(position.getQuantity() * position.getAveragePrice())))
        return Decimal('0')

    def get_market_summary(self, symbol: str) -> dict:
        """Get market summary including order book depth and recent trades"""
        order_book = self.get_order_book(symbol)  # Using updated get_order_book method
        orders = order_book.getOrders()
        
        buys = [o for o in orders if o.getSide() == Side.BUY]
        sells = [o for o in orders if o.getSide() == Side.SELL]

        return {
            'symbol': symbol,
            'bid': max([o.getPrice().value for o in buys]) if buys else None,
            'ask': min([o.getPrice().value for o in sells]) if sells else None,
            'buy_depth': sum(o.getQuantity() for o in buys),
            'sell_depth': sum(o.getQuantity() for o in sells),
            'last_trade': self._get_last_trade(symbol),
            'volume_24h': self._get_24h_volume(symbol)
        }

    def _get_last_trade(self, symbol: str) -> Optional[dict]:
        trade = TradeModel.objects.filter(symbol=symbol).order_by('-timestamp').first()
        if trade:
            return {
                'price': float(trade.price),
                'quantity': float(trade.quantity),
                'timestamp': trade.timestamp
            }
        return None