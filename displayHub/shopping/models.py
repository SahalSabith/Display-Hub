from django.db import models
from django.contrib.auth.models import User
from userProfile.models import Address
from adminManagements.models import Products,Varients

# Create your models here.
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)
    updatedAt = models.DateField(auto_now=True)

    def cartTotal(self):
        total = 0
        cartItems = CartItem.objects.filter(cartId=self)
        for item in cartItems:
            total += item.cartItemTotal()
        return total 
    
    def __str__(self):
        id = str(self.pk)
        return id


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    productId = models.ForeignKey(Products,on_delete=models.CASCADE)
    varientId = models.ForeignKey(Varients,on_delete=models.CASCADE)
    quantity = models.IntegerField()
    cartId = models.ForeignKey(Cart,on_delete=models.CASCADE)

    def cartItemTotal(self):
        total = self.varientId.price * self.quantity
        return total
    
    def __str__(self):
        id = str(self.pk)
        return id

class Order(models.Model):
    statusChoices = [
        ('dispatched', 'Dispatched'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
        ('returned', 'Returned'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('refunded', 'Refunded')
    ]
    orderStatus = models.CharField(max_length=20,choices=statusChoices,default='dispatched')
    orderedAt = models.DateTimeField(auto_now=True)
    userId = models.ForeignKey(User,related_name='userId',on_delete=models.CASCADE)
    addressId = models.ForeignKey(Address,on_delete=models.CASCADE)
    payments = [
        ('cashOnDelivery','CashOnDelivey'),
        ('wallet','Wallet'),
        ('internetBanking','InternetBanking')
    ]
    paymentMethod = models.CharField(max_length=20,choices=payments,default='cashOnDelivery')
    orderNo = models.CharField(max_length=10,unique=True)
    totalPrice = models.IntegerField(default=0)
    cancelReason = models.TextField()

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    productId = models.ForeignKey(Products,on_delete=models.CASCADE)
    varientId = models.ForeignKey(Varients,on_delete=models.CASCADE) 
    quantity = models.IntegerField()
    totalPrice = models.IntegerField(default=0)
    orderItemId = models.ForeignKey(Order,related_name='orderItemId',on_delete=models.CASCADE)