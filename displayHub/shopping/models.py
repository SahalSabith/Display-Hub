from django.db import models
from django.contrib.auth.models import User
from userProfile.models import Address

# Create your models here.
class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)
    updatedAt = models.DateField(auto_now=True)

    def cartTotal(self):
        total = 0
        cartItems = CartItem.objects.filter(cartId=self)
        for item in cartItems:
            total += item.productTotal()
        return total 


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    #product a here
    quantity = models.IntegerField()
    cartId = models.ForeignKey(Cart,on_delete=models.CASCADE)

    def productTotal(self):
        return self.quantity * self.product.price

class Order(models.Model):
    statusChoices = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
        ('returned', 'Returned'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('awaiting_payment', 'Awaiting Payment'),
    ]
    orderStatus = models.CharField(max_length=20,choices=statusChoices,default='pending')
    orderedAt = models.DateTimeField(auto_now=True)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)
    addressId = models.ForeignKey(Address,on_delete=models.CASCADE)
    payments = [
        ('cashOnDelivery','CashOnDelivey'),
        ('wallet','Wallet'),
        ('internetBanking','InternetBanking')
    ]
    paymentMethod = models.CharField(max_length=20,choices=payments,default='cashOnDelivery')
    orderNo = models.CharField(max_length=10,unique=True)
    totalPrice = models.IntegerField(default=0)


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    #product hefre also 
    quantity = models.IntegerField()
    orderId = models.ForeignKey(Order,related_name='orderId',on_delete=models.CASCADE)
    totalPrice = models.IntegerField(default=0)

