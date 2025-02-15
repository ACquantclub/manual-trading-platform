from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('orderbook/', views.orderbook_view, name='orderbook'),
    path('positions/', views.positions_view, name='positions'),
    path('place-order/', views.place_order, name='place_order'),
    path('cancel-order/<uuid:order_id>/', views.cancel_order, name='cancel_order'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
]