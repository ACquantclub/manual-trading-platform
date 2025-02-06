from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import TradingUser, OrderModel, TradeModel
from trading import Market, Side, Price
from decimal import Decimal

market = Market()  # Global market instance

@login_required
def submit_order(request):
    if request.method == 'POST':
        user = request.user.tradinguser
        symbol = request.POST.get('symbol')
        side = request.POST.get('side')
        quantity = Decimal(request.POST.get('quantity'))
        price = Decimal(request.POST.get('price'))

        # Create and save order
        order = OrderModel.objects.create(
            user=user,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price
        )

        # Add to trading engine
        trading_order = order.to_trading_order()
        market.addOrder(trading_order)

        # Match orders
        trades = market.matchOrders(symbol)
        
        # Save trades to database
        for trade in trades:
            TradeModel.objects.create(
                buy_order=OrderModel.objects.get(id=trade.getBuyOrderId()),
                sell_order=OrderModel.objects.get(id=trade.getSellOrderId()),
                symbol=trade.getSymbol(),
                quantity=trade.getQuantity(),
                price=trade.getPrice()
            )

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)

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