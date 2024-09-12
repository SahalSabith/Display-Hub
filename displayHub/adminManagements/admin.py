from django.contrib import admin
from .models import Category,Brand,Products,Size,RefreshRate,Varients
# Register your models here.
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(Products)
admin.site.register(Size)
admin.site.register(RefreshRate)
admin.site.register(Varients)