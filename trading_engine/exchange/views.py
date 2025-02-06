from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from .market_manager import MarketManager
from .models import TradingUser, OrderModel, TradeModel
from decimal import Decimal
import logging
from datetime import datetime, timedelta
from trading import Side

logger = logging.getLogger(__name__)
market_manager = MarketManager()

@login_required
def dashboard(request):
    """Enhanced dashboard with market overview"""
    user = request.user.tradinguser
    
    # Get user's positions
    positions = user.get_positions()
    
    # Get active orders
    active_orders = OrderModel.objects.filter(
        user=user,
        status='NEW'
    ).order_by('-created_at')
    
    # Get market summaries for user's traded symbols
    traded_symbols = OrderModel.objects.filter(user=user).values_list('symbol', flat=True).distinct()
    market_summaries = {
        symbol: market_manager.get_market_summary(symbol)
        for symbol in traded_symbols
    }
    
    context = {
        'balance': user.balance,
        'positions': positions,
        'active_orders': active_orders,
        'market_summaries': market_summaries
    }
    
    return render(request, 'exchange/dashboard.html', context)

@login_required
def submit_order(request):
    if request.method == 'POST':
        try:
            user = request.user.tradinguser
            symbol = request.POST.get('symbol')
            side = request.POST.get('side')
            quantity = Decimal(request.POST.get('quantity'))
            price = Decimal(request.POST.get('price'))

            # Submit order through market manager
            order, trades = market_manager.submit_order(
                user=user,
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )

            return JsonResponse({
                'status': 'success',
                'order_id': order.id,
                'trades': [
                    {
                        'id': trade.id,
                        'price': str(trade.price),
                        'quantity': str(trade.quantity),
                        'timestamp': trade.timestamp.isoformat(),
                        'counterparty': trade.buy_order.user.user.username 
                            if trade.sell_order.user == user 
                            else trade.sell_order.user.user.username
                    } for trade in trades
                ] if trades else [],
                'remaining_balance': str(user.balance)
            })

        except ValueError as e:
            logger.warning(f"Order validation failed: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        except Exception as e:
            logger.error(f"Order submission failed: {e}")
            return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
def order_book(request, symbol):
    try:
        order_book = market_manager.get_order_book(symbol)
        if not order_book:
            # Return empty order book instead of 404
            return JsonResponse({
                'symbol': symbol,
                'bids': [],
                'asks': [],
                'last_trade': None
            })
            
        orders = order_book.getOrders()
        buys = [o for o in orders if o.getSide() == Side.BUY]
        sells = [o for o in orders if o.getSide() == Side.SELL]
        
        return JsonResponse({
            'symbol': symbol,
            'bids': [
                {
                    'price': o.getPrice().getValue(),
                    'quantity': o.getQuantity(),
                    'total_orders': len([x for x in buys if x.getPrice().getValue() == o.getPrice().getValue()])
                } for o in sorted(buys, key=lambda x: (-x.getPrice().getValue(), x.getId()))
            ],
            'asks': [
                {
                    'price': o.getPrice().getValue(),
                    'quantity': o.getQuantity(),
                    'total_orders': len([x for x in sells if x.getPrice().getValue() == o.getPrice().getValue()])
                } for o in sorted(sells, key=lambda x: (x.getPrice().getValue(), x.getId()))
            ],
            'last_trade': market_manager._get_last_trade(symbol)
        })
    except Exception as e:
        logger.error(f"Failed to fetch order book: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
    
@login_required
def cancel_order(request, order_id):
    try:
        order = OrderModel.objects.get(id=order_id, user=request.user.tradinguser)
        if order.status != 'NEW':
            return JsonResponse({'status': 'error', 'message': 'Order cannot be cancelled'}, status=400)
        
        try:
            # Convert to trading order and cancel
            trading_order = order.to_trading_order()
            market_manager.market.cancelOrder(trading_order)
            
            # Update order status
            order.status = 'CANCELLED'
            order.save()
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            logger.error(f"Trading engine cancel failed: {e}")
            return JsonResponse({'status': 'error', 'message': 'Failed to cancel order in trading engine'}, status=500)
            
    except OrderModel.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Order not found'}, status=404)
    except Exception as e:
        logger.error(f"Failed to cancel order: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)
@login_required
def user_orders(request):
    """Get user's order history"""
    try:
        orders = OrderModel.objects.filter(user=request.user.tradinguser).order_by('-created_at')
        return JsonResponse({
            'orders': [
                {
                    'id': order.id,
                    'symbol': order.symbol,
                    'side': order.side,
                    'quantity': str(order.quantity),
                    'price': str(order.price),
                    'status': order.status,
                    'created_at': order.created_at.isoformat()
                } for order in orders
            ]
        })
    except Exception as e:
        logger.error(f"Failed to fetch user orders: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

@login_required
def market_summary(request, symbol):
    """Get detailed market summary for a symbol"""
    try:
        summary = market_manager.get_market_summary(symbol)
        if summary:
            return JsonResponse(summary)
        return JsonResponse({'status': 'error', 'message': 'Symbol not found'}, status=404)
    except Exception as e:
        logger.error(f"Failed to fetch market summary: {e}")
        return JsonResponse({'status': 'error', 'message': 'Internal server error'}, status=500)

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'exchange/register.html')

        # Create user and trading user
        user = User.objects.create_user(username=username, password=password, email=email)
        TradingUser.objects.create(user=user)
        
        # Log the user in
        login(request, user)
        return redirect('dashboard')

    return render(request, 'exchange/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'exchange/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    return render(request, 'exchange/dashboard.html')