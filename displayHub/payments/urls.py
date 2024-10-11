"""
URL configuration for displayHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('repayment/', views.repayment, name='repayment'),
    path("razorpay/callback/", views.razorpay_callback, name="razorpay_callback"),
    path('get_wallet_balance/', views.get_wallet_balance, name='get_wallet_balance'),
    path('process_wallet_payment/', views.process_wallet_payment, name='process_wallet_payment'),
    path('cart/checkout',views.checkOut,name='checkOut'),
    path('orderSuccess/',views.orderSuccess,name="successPage")
]