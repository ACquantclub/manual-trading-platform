from django.core.management.base import BaseCommand
from exchange.market_manager import MarketManager
from exchange.models import TradingPair, TradeModel
from django.utils.timezone import localtime
import trading

class Command(BaseCommand):
    help = 'Shows the current orderbook and recent trades for a trading pair'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Trading pair symbol (e.g., BTCUSD)')

    def handle(self, *args, **kwargs):
        symbol = kwargs['symbol'].upper()
        try:
            trading_pair = TradingPair.objects.get(symbol=symbol)
            market_manager = MarketManager()
            
            # Show Orderbook
            try:
                market_manager.ensure_orderbook(symbol)
                orderbook = market_manager.market.getOrderBook(symbol)
                orders = orderbook.getOrders()
                bids = []
                asks = []
                for order in orders:
                    if order.getSide() == trading.Side.BUY:
                        bids.append((order.getPrice().value, order.getQuantity()))
                    else:
                        asks.append((order.getPrice().value, order.getQuantity()))

                self.stdout.write(self.style.SUCCESS(f'\nOrderbook for {symbol}:'))
                if not bids and not asks:
                    self.stdout.write(self.style.WARNING('Orderbook is empty'))
                else:
                    self.stdout.write('\nBids:')
                    for price, qty in sorted(bids, reverse=True):
                        self.stdout.write(f'  {qty:.8f} @ {price:.2f}')
                    
                    self.stdout.write('\nAsks:')
                    for price, qty in sorted(asks):
                        self.stdout.write(f'  {qty:.8f} @ {price:.2f}')

            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error accessing orderbook: {str(e)}'))

            # Show Recent Trades
            trades = TradeModel.objects.filter(trading_pair=trading_pair).order_by('-timestamp')[:5]
            
            if trades:
                self.stdout.write(self.style.SUCCESS('\nRecent Trades:'))
                for trade in trades:
                    time = localtime(trade.timestamp).strftime('%H:%M:%S')
                    self.stdout.write(
                        f'  {time} - {trade.quantity:.8f} @ {trade.price:.2f}'
                    )
            else:
                self.stdout.write(self.style.WARNING('\nNo recent trades'))

        except TradingPair.DoesNotExist:
            available_pairs = TradingPair.objects.values_list('symbol', flat=True)
            self.stdout.write(
                self.style.ERROR(
                    f'Trading pair {symbol} not found\n'
                    f'Available pairs: {", ".join(available_pairs)}'
                )
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))