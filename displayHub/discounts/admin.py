from django.contrib import admin
from . models import Coupon,BrandOffer,ProductOffer,CouponUsage

# Register your models here.
admin.site.register(Coupon)
admin.site.register(CouponUsage)
admin.site.register(BrandOffer)
admin.site.register(ProductOffer)