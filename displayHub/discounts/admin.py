from django.contrib import admin
from . models import Coupon,BrandOffer,ProductOffer

# Register your models here.
admin.site.register(Coupon)
admin.site.register(BrandOffer)
admin.site.register(ProductOffer)