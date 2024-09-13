from django.db import models

# Create your models here.
class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20,unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Brand(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=15,unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class Size(models.Model):
    id = models.AutoField(primary_key=True)
    size = models.IntegerField()

    def __str__(self):
        sizeStr = str(self.size)
        return sizeStr
    

class RefreshRate(models.Model):
    id = models.AutoField(primary_key=True)
    refreshRate = models.IntegerField()

    def __str__(self):
        refreshRateStr = str(self.refreshRate)
        return refreshRateStr
    

class Products(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50,unique=True)
    createdAt = models.DateTimeField(auto_now=True)
    resolution = models.IntegerField()
    status = models.BooleanField(default=True)
    category = models.ForeignKey(Category,related_name='brand',on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand,related_name='brand',on_delete=models.CASCADE)
    image1 = models.ImageField(upload_to='media/',null=True, blank=True)
    image2 = models.ImageField(upload_to='media/',null=True, blank=True)
    image3 = models.ImageField(upload_to='media/',null=True, blank=True)
    image4 = models.ImageField(upload_to='media/',null=True, blank=True)

    def __str__(self):
        return str(self.pk)
    
class Varients(models.Model):
    id = models.AutoField(primary_key=True)
    size = models.ForeignKey(Size,on_delete=models.CASCADE)
    refreshRate = models.ForeignKey(RefreshRate,on_delete=models.CASCADE)
    price = models.FloatField()
    stock = models.IntegerField()
    product = models.ForeignKey(Products,related_name='varient',on_delete=models.CASCADE)