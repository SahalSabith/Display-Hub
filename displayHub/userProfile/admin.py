from django.contrib import admin
from . models import Address,Transaction,Wallet

# Register your models here.
admin.site.register(Address)
admin.site.register(Transaction)
admin.site.register(Wallet)