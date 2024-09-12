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