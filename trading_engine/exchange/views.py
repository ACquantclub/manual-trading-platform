from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from decimal import Decimal
from .models import OrderModel, TradingPair, Balance
from .market_manager import MarketManager
import json
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import trading
from django.views.decorators.http import require_http_methods
import logging
logger = logging.getLogger(__name__)

market_manager = MarketManager()

@login_required
@csrf_exempt
def place_order(request):
    try:
        with transaction.atomic():
            data = json.loads(request.body)
            
            # Validate side using enum
            if data['side'] not in [side.name for side in trading.Side]:
                return JsonResponse({'error': 'Invalid side'}, status=400)
            
            # Validate required fields
            required_fields = ['symbol', 'side', 'quantity', 'price']
            if not all(field in data for field in required_fields):
                return JsonResponse({'error': 'Missing required fields'}, status=400)
            
            # Validate values
            if data['quantity'] <= 0:
                return JsonResponse({'error': 'Quantity must be positive'}, status=400)
            if data['price'] <= 0:
                return JsonResponse({'error': 'Price must be positive'}, status=400)
            if data['side'] not in ['BUY', 'SELL']:
                return JsonResponse({'error': 'Invalid side'}, status=400)
            
            # Check balance
            trading_pair = TradingPair.objects.get(symbol=data['symbol'])
            if data['side'] == 'BUY':
                required_currency = trading_pair.quote_currency
                required_amount = Decimal(str(data['price'])) * Decimal(str(data['quantity']))
            else:
                required_currency = trading_pair.base_currency
                required_amount = Decimal(str(data['quantity']))
                
            try:
                balance = Balance.objects.get(
                    user=request.user, 
                    currency=required_currency
                )
                if balance.amount < required_amount:
                    return JsonResponse({
                        'error': f'Insufficient {required_currency} balance'
                    }, status=400)
                    
                # Reserve the balance
                balance.amount -= required_amount
                balance.save()
                
            except Balance.DoesNotExist:
                return JsonResponse({
                    'error': f'No {required_currency} balance'
                }, status=400)
            
            # Create and process order
            order = OrderModel.objects.create(
                user=request.user,
                trading_pair=trading_pair,
                side=data['side'],
                quantity=data['quantity'],
                price=data['price'],
                status=trading.OrderStatus.NEW.name  # Use enum value
            )
            
            trades = market_manager.add_order(order)
            
            # If no trades, the order stays in the book
            if not trades:
                return JsonResponse({
                    'order_id': str(order.order_id),
                    'status': 'success',
                    'trades': []
                })
                
            # Process trades and update balances
            for trade in trades:
                update_balances_for_trade(trade, trading_pair)
                
            return JsonResponse({
                'order_id': str(order.order_id),
                'status': 'success',
                'trades': [
                    {
                        'price': trade.getPrice().value,
                        'quantity': trade.getQuantity(),
                        'timestamp': trade.getTimestamp()
                    } for trade in trades
                ]
            })
            
    except TradingPair.DoesNotExist:
        return JsonResponse({'error': 'Invalid trading pair'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def update_balances_for_trade(trade, trading_pair):
    """Helper function to update balances after a trade"""
    quantity = Decimal(str(trade.getQuantity()))
    price = Decimal(str(trade.getPrice().value))
    total = quantity * price
    
    # Get orders
    buy_order = OrderModel.objects.get(order_id=trade.getBuyOrderId())
    sell_order = OrderModel.objects.get(order_id=trade.getSellOrderId())
    
    # Update buyer balances
    buyer_quote_balance = Balance.objects.get(
        user=buy_order.user,
        currency=trading_pair.quote_currency
    )
    buyer_base_balance = Balance.objects.get_or_create(
        user=buy_order.user,
        currency=trading_pair.base_currency
    )[0]
    
    # Update seller balances
    seller_quote_balance = Balance.objects.get_or_create(
        user=sell_order.user,
        currency=trading_pair.quote_currency
    )[0]
    seller_base_balance = Balance.objects.get(
        user=sell_order.user,
        currency=trading_pair.base_currency
    )
    
    # Execute the transfer
    buyer_quote_balance.amount -= total
    buyer_base_balance.amount += quantity
    seller_quote_balance.amount += total
    seller_base_balance.amount -= quantity
    
    buyer_quote_balance.save()
    buyer_base_balance.save()
    seller_quote_balance.save()
    seller_base_balance.save()
    
@login_required
def get_positions(request):
    try:
        positions = market_manager.market.getAllPositions()
        return JsonResponse({
            'positions': [{
                'symbol': pos.getSymbol(),
                'quantity': pos.getQuantity(),
                'average_price': pos.getAveragePrice().value
            } for pos in positions]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@login_required
def get_orderbook(request, symbol):
    try:
        orderbook = market_manager.market.getOrderBook(symbol)
        orders = orderbook.getOrders()
        
        bids = []
        asks = []
        for order in orders:
            order_data = {
                'price': order.getPrice().value,
                'quantity': order.getQuantity()
            }
            if order.getSide() == trading.Side.BUY:
                bids.append(order_data)
            else:
                asks.append(order_data)
                
        return JsonResponse({
            'symbol': symbol,
            'bids': sorted(bids, key=lambda x: x['price'], reverse=True),
            'asks': sorted(asks, key=lambda x: x['price'])
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=404)
    
@login_required
@csrf_exempt
def cancel_order(request, order_id):
    try:
        with transaction.atomic():
            order = OrderModel.objects.select_for_update().get(
                order_id=order_id, 
                user=request.user,
                status=trading.OrderStatus.NEW.name  # Use enum value
            )
            
            # Refund the reserved balance
            if order.side == 'BUY':
                required_currency = order.trading_pair.quote_currency
                required_amount = order.price * order.quantity
            else:
                required_currency = order.trading_pair.base_currency
                required_amount = order.quantity
                
            balance = Balance.objects.select_for_update().get(
                user=request.user,
                currency=required_currency
            )
            balance.amount += required_amount
            balance.save()
            
            # Cancel in trading engine
            trading_order = order.to_trading_order()
            market_manager.market.cancelOrder(trading_order.getId())
            
            # Update order status using enum
            order.status = trading.OrderStatus.CANCELLED.name
            order.save()
            
            return JsonResponse({'status': 'success'})
            
    except OrderModel.DoesNotExist:
        return JsonResponse({'error': 'Order not found or already cancelled'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def home(request):
    # Initialize orderbooks for all trading pairs
    for pair in TradingPair.objects.all():
        market_manager.ensure_orderbook(pair.symbol)

    trading_pairs_data = list(TradingPair.objects.values('symbol', 'base_currency', 'quote_currency'))
    orders_data = list(OrderModel.objects.filter(user=request.user).order_by('-created_at').values(
        'order_id',
        'trading_pair__symbol',
        'side',
        'quantity',
        'price',
        'status'
    ))

    return render(request, 'exchange/home.html', {
        'trading_pairs': TradingPair.objects.all(),  # For template iteration
        'trading_pairs_json': trading_pairs_data,    # For JavaScript
        'orders': OrderModel.objects.filter(user=request.user).order_by('-created_at'),  # For template iteration
        'orders_json': orders_data,                  # For JavaScript
        'balances': Balance.objects.filter(user=request.user).order_by('currency')
    })
    
@login_required
def orderbook_view(request):
    symbol = request.GET.get('symbol', 'BTCUSD')
    orderbook_data = None
    
    try:
        orderbook = market_manager.market.getOrderBook(symbol)
        orders = orderbook.getOrders()
        
        bids = []
        asks = []
        for order in orders:
            order_data = {
                'price': order.getPrice().value,
                'quantity': order.getQuantity()
            }
            if order.getSide() == trading.Side.BUY:
                bids.append(order_data)
            else:
                asks.append(order_data)
                
        orderbook_data = {
            'bids': sorted(bids, key=lambda x: x['price'], reverse=True),
            'asks': sorted(asks, key=lambda x: x['price'])
        }
    except Exception:
        pass
    
    return render(request, 'exchange/orderbook.html', {
        'trading_pairs': TradingPair.objects.all(),
        'selected_symbol': symbol,
        'orderbook': orderbook_data
    })

@login_required
def positions_view(request):
    try:
        positions = market_manager.market.getAllPositions()
        positions_data = [{
            'symbol': pos.getSymbol(),
            'quantity': pos.getQuantity(),
            'average_price': pos.getAveragePrice().value
        } for pos in positions]
    except Exception:
        positions_data = []
        
    return render(request, 'exchange/positions.html', {
        'positions': positions_data
    })
    
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            return render(request, 'exchange/register.html', {'error': 'Passwords do not match'})
            
        if User.objects.filter(username=username).exists():
            return render(request, 'exchange/register.html', {'error': 'Username already exists'})
        
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(username=username, password=password1)
                
                # Initial portfolio balances
                initial_balances = {
                    'USD': 1000000.00,  # $1M USD
                    'AAPL': 100.0,      # 100 shares of Apple
                    'MSFT': 100.0,      # 100 shares of Microsoft
                    'GOOGL': 100.0,     # 100 shares of Google
                    'AMZN': 100.0,      # 100 shares of Amazon
                    'NVDA': 100.0,      # 100 shares of NVIDIA
                    'META': 100.0,      # 100 shares of Meta
                    'TSLA': 100.0,      # 100 shares of Tesla
                    'JPM': 100.0,       # 100 shares of JPMorgan
                    'VIS': 100.0,       # 100 shares of Visa
                    'KO': 100.0,        # 100 shares of Coca-Cola
                    'WMT': 100.0,       # 100 shares of Walmart
                    'DIS': 100.0        # 100 shares of Disney
                }
                
                # Create balances for all stocks
                for currency, amount in initial_balances.items():
                    Balance.objects.create(
                        user=user,
                        currency=currency,
                        amount=amount
                    )
                
                login(request, user)
                return redirect('home')
                
        except Exception as e:
            return render(request, 'exchange/register.html', {'error': f'Registration failed: {str(e)}'})
        
    return render(request, 'exchange/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'exchange/login.html', {'error': 'Invalid credentials'})
            
    return render(request, 'exchange/login.html')

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    return redirect('login')