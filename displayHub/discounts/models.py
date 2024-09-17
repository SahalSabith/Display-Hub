from django.db import models
from adminManagements.models import Category,Products,Brand

# Create your models here.
class Coupon(models.Model):
    couponCode = models.CharField(max_length=40, unique=True)
    validFrom = models.DateField()
    validTo = models.DateField()
    discountTypeChoice = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed'),
    ]
    discountType = models.CharField(choices=discountTypeChoice)
    discountValue = models.FloatField(null=True, blank=True)
    fixedDiscountValue = models.FloatField(null=True, blank=True)
    minPurchaseAmount = models.FloatField()
    maxDiscountAmount = models.FloatField()
    usageLimit = models.IntegerField()
    usedCount = models.IntegerField(default=0)
    status = models.BooleanField(default=True)
    applicableProducts = models.ManyToManyField(Products, related_name='coupon')
    applicableCategory = models.ManyToManyField(Category, related_name='coupon')
    applicableBrand = models.ManyToManyField(Brand, related_name='coupon')

    def __str__(self):
        return self.couponCode