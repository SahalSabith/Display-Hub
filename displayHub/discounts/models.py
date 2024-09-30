from django.db import models
from adminManagements.models import Category,Products,Brand
from django.contrib.auth.models import User

# Create your models here.
class Coupon(models.Model):
    couponCode = models.CharField(max_length=40, unique=True)
    validFrom = models.DateField(auto_now=True)
    validTo = models.DateField()
    discountValue = models.FloatField(null=True, blank=True)
    minPurchaseAmount = models.FloatField()
    maxPurchaseAmount = models.FloatField()
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.couponCode
    
class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)

class ProductOffer(models.Model):
    name = models.CharField(max_length=255)
    discountValue = models.FloatField()
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    applicableProducts = models.ForeignKey(Products, related_name='productoffer', blank=True,on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    createdAt = models.DateField(auto_now=True)

class BrandOffer(models.Model):
    name = models.CharField(max_length=255)
    discountValue = models.FloatField()
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    applicableBrand = models.ForeignKey(Brand, related_name='brandoffer', blank=True,on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    createdAt = models.DateField(auto_now=True)