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
    path('cart/',views.cart,name='cart'),
    path('shop/',views.products,name='shop'),
    path('product/<int:pId>/',views.productInfo,name='productInfo'),
    path('product/addToCart/<int:pId>/',views.addToCart,name="addToCart"),
    path('removeItem/<int:cId>/',views.removeCart,name='remove'),
    path('cart/checkout',views.checkOut,name='checkOut'),
    path('account/orderDetails/<int:oId>',views.orderDetails,name='orderDetails'),
    path('account/cancel/<int:oId>/',views.cancelOrder,name='cancelOrder'),
    path('cart/quantityUpdate',views.updateQuantity,name='updateQuantity')
]
