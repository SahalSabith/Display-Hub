from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Address(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField()
    phone = models.CharField()
    houseName = models.CharField()
    city = models.CharField()
    district = models.CharField()
    state = models.CharField()
    zipCode = models.CharField()
    userId = models.ForeignKey(User,on_delete=models.CASCADE)

class Wallet(models.Model):
    userId = models.ForeignKey(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        id = str(self.pk)
        return id
    

class Transaction(models.Model):
    walletId = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    typeChoices = [
        ('refund', 'Refund'),
        ('addMoney', 'Added Money'),
    ]
    transactionType = models.CharField(max_length=20, choices=typeChoices)
    amount = models.FloatField()
    createdAt = models.DateTimeField(auto_now_add=True)