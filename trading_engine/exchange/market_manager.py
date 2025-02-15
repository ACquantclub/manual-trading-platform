from threading import Lock
import logging
from trading import Market, OrderStatus, Side, Price, Order
from .models import OrderModel, TradeModel, TradingPair, Balance
from django.db import transaction
from django.db.models import Q

logger = logging.getLogger(__name__)

class MarketManager:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Initialize the market and load all trading pairs"""
        self._market = Market()
        self._operation_lock = Lock()
        self._initialized_pairs = set()
        
        # Initialize orderbooks for all trading pairs
        for pair in TradingPair.objects.all():
            self._ensure_orderbook_exists(pair.symbol)

    @property
    def market(self):
        return self._market
    
    def _ensure_orderbook_exists(self, symbol):
        """Ensures orderbook exists for the given symbol and initializes it if needed.
        
        Args:
            symbol (str): The trading pair symbol (e.g., 'BTCUSD')
            
        Raises:
            RuntimeError: If orderbook creation fails
        """
        if symbol not in self._initialized_pairs:
            with self._operation_lock:
                try:
                    # Check again in case another thread initialized it
                    if symbol not in self._initialized_pairs:
                        if not self._market.hasOrderBook(symbol):
                            # Create valid dummy order to initialize orderbook
                            dummy_price = Price()
                            dummy_price.value = 1.0  # Valid non-zero price
                            dummy_order = Order(symbol, Side.BUY, 0.1, dummy_price)  # Valid non-zero quantity
                            self._market.addOrder(dummy_order)
                            self._market.cancelOrder(dummy_order.getId())
                        
                        # Verify orderbook was created
                        if not self._market.hasOrderBook(symbol):
                            raise RuntimeError(f"Failed to create orderbook for {symbol}")
                            
                        self._initialized_pairs.add(symbol)
                        logger.info(f"Initialized orderbook for {symbol}")
                except Exception as e:
                    logger.error(f"Failed to initialize orderbook for {symbol}: {str(e)}")
                    raise RuntimeError(f"Failed to initialize orderbook: {str(e)}")
    
    def add_order(self, order_model):
        """Add an order to the market and process any resulting trades"""
        with transaction.atomic():
            try:
                # Ensure orderbook exists
                symbol = order_model.trading_pair.symbol
                self._ensure_orderbook_exists(symbol)
                
                # Validate balance before adding order
                if order_model.side == 'BUY':
                    required_balance = order_model.price * order_model.quantity
                    balance = Balance.objects.select_for_update().get(
                        user=order_model.user,
                        currency=order_model.trading_pair.quote_currency
                    )
                    if balance.amount < required_balance:
                        raise ValueError("Insufficient balance for buy order")
                else:  # SELL
                    balance = Balance.objects.select_for_update().get(
                        user=order_model.user,
                        currency=order_model.trading_pair.base_currency
                    )
                    if balance.amount < order_model.quantity:
                        raise ValueError("Insufficient balance for sell order")

                # Lock the order for update
                order_model = OrderModel.objects.select_for_update().get(pk=order_model.pk)
                order_model.status = OrderStatus.NEW.name
                order_model.save()

                # Convert to trading order
                trading_order = order_model.to_trading_order()
                
                with self._operation_lock:
                    try:
                        # Add order to market
                        self._market.addOrder(trading_order)
                        # Match orders
                        trades = self._market.matchOrders(symbol)
                        
                        if trades:
                            logger.info(f"Order {order_model.order_id} matched with {len(trades)} trades")
                            self._process_trades(trades, order_model.trading_pair)
                        
                        return trades
                        
                    except Exception as e:
                        logger.error(f"Trading engine error: {str(e)}")
                        order_model.status = OrderStatus.REJECTED.name
                        order_model.save()
                        raise
                    
            except Exception as e:
                logger.error(f"Error processing order {order_model.order_id}: {str(e)}", exc_info=True)
                order_model.status = OrderStatus.REJECTED.name
                order_model.save()
                raise

    def _process_trades(self, trades, trading_pair):
        """Process trades in a thread-safe manner"""
        with transaction.atomic():
            for trade in trades:
                try:
                    # Get both orders in a single query with select_for_update
                    buy_id = str(trade.getBuyOrderId())
                    sell_id = str(trade.getSellOrderId())
                    orders = OrderModel.objects.select_for_update().filter(
                        order_id__in=[buy_id, sell_id]
                    ).select_related('user')

                    if len(orders) != 2:
                        logger.error(f"Could not find both orders for trade processing: {buy_id}, {sell_id}")
                        continue

                    # Get buy and sell orders
                    buy_order = next(o for o in orders if o.order_id == buy_id)
                    sell_order = next(o for o in orders if o.order_id == sell_id)

                    # Calculate trade details
                    trade_value = trade.getPrice().value * trade.getQuantity()
                    trade_quantity = trade.getQuantity()

                    # Update balances first
                    balances = Balance.objects.select_for_update().filter(
                        (Q(user=buy_order.user) & Q(currency__in=[trading_pair.quote_currency, trading_pair.base_currency])) |
                        (Q(user=sell_order.user) & Q(currency__in=[trading_pair.quote_currency, trading_pair.base_currency]))
                    )

                    balance_map = {(b.user.id, b.currency): b for b in balances}

                    # Update buyer balances
                    buyer_quote = balance_map.get((buy_order.user.id, trading_pair.quote_currency))
                    buyer_base = balance_map.get((buy_order.user.id, trading_pair.base_currency))
                    if buyer_quote:
                        buyer_quote.amount -= trade_value
                    if buyer_base:
                        buyer_base.amount += trade_quantity

                    # Update seller balances
                    seller_base = balance_map.get((sell_order.user.id, trading_pair.base_currency))
                    seller_quote = balance_map.get((sell_order.user.id, trading_pair.quote_currency))
                    if seller_base:
                        seller_base.amount -= trade_quantity
                    if seller_quote:
                        seller_quote.amount += trade_value

                    # Save all balances
                    Balance.objects.bulk_update(balances, ['amount'])

                    # Update order statuses
                    buy_order.status = OrderStatus.FILLED.name
                    sell_order.status = OrderStatus.FILLED.name
                    buy_order.save()
                    sell_order.save()

                    # Create trade record
                    TradeModel.objects.create(
                        buy_order=buy_order,
                        sell_order=sell_order,
                        trading_pair=trading_pair,
                        quantity=trade_quantity,
                        price=trade.getPrice().value
                    )

                    logger.info(f"Processed trade: {trade_quantity} {trading_pair.symbol} @ {trade.getPrice().value}")

                except Exception as e:
                    logger.error(f"Error processing trade: {str(e)}", exc_info=True)
                    continue