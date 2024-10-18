from django.db import models
from adminManagements.models import Products,Varients
from django.contrib.auth.models import User

# Create your models here.
class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    varientId = models.ForeignKey(Varients,on_delete=models.CASCADE)
    userId = models.ForeignKey(User,on_delete=models.CASCADE)

class Subscribers(models.Model):
    email = models.CharField()