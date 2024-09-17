from django.shortcuts import render, redirect,HttpResponse
from .models import Coupon
from django.views.decorators.cache import never_cache
from adminManagements.models import Category, Brand, Products
from .models import Coupon
from datetime import datetime

@never_cache
def addCoupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('couponCode')
        valid_from = request.POST.get('validFrom')
        valid_to = request.POST.get('validTo')
        discount_type = request.POST.get('discountType')

        discount_value = request.POST.get('discountValue') or None
        fixed_discount_value = request.POST.get('fixedDiscountValue') or None

        if discount_type == 'fixed' and fixed_discount_value:
            fixed_discount_value = float(fixed_discount_value)
            discount_value = None
        elif discount_type == 'percentage' and discount_value:
            discount_value = float(discount_value)
            fixed_discount_value = None
        else:
            discount_value = None
            fixed_discount_value = None

        min_purchase_amount = request.POST.get('minPurchaseAmount')
        max_discount_amount = request.POST.get('maxDiscountAmount')
        usage_limit = request.POST.get('usageLimit')
        applicable_brand = request.POST.getlist('applicableBrand')
        applicable_category = request.POST.getlist('applicableCategory')
        applicable_products = request.POST.getlist('applicableProducts')

        new_coupon = Coupon.objects.create(
            couponCode=coupon_code,
            validFrom=valid_from,
            validTo=valid_to,
            discountType=discount_type,
            discountValue=discount_value,
            fixedDiscountValue=fixed_discount_value,
            minPurchaseAmount=min_purchase_amount,
            maxDiscountAmount=max_discount_amount,
            usageLimit=usage_limit,
        )

        new_coupon.applicableProducts.set(applicable_products)
        new_coupon.applicableBrand.set(applicable_brand)
        new_coupon.applicableCategory.set(applicable_category)

        return redirect('addCoupon')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Products.objects.all()
    coupon = Coupon.objects.all()

    context = {
        'categories': categories,
        'brands': brands,
        'product': products,
        'coupon': coupon,
    }

    return render(request, 'couponManagement.html', context)

@never_cache
def editCoupon(request, cId):
    if request.method == 'POST':
        couponCode = request.POST.get('couponCode')
        validFrom = request.POST.get('validFrom')
        validTo = request.POST.get('validTo')
        discountType = request.POST.get('discountType')

        discountValue = request.POST.get('discountValue') or None
        fixedDiscountValue = request.POST.get('fixedDiscountValue') or None

        if discountType == 'fixed' and fixedDiscountValue:
            fixedDiscountValue = float(fixedDiscountValue)
            discountValue = None
        elif discountType == 'percentage' and discountValue:
            discountValue = float(discountValue)
            fixedDiscountValue = None
        else:
            discountValue = None
            fixedDiscountValue = None

        minPurchaseAmount = request.POST.get('minPurchaseAmount')
        maxDiscountAmount = request.POST.get('maxDiscountAmount')
        usageLimit = request.POST.get('usageLimit')
        applicableBrand = request.POST.getlist('applicableBrand')
        applicableCategory = request.POST.getlist('applicableCategory')
        applicableProducts = request.POST.getlist('applicableProducts')

        try:
            coupon = Coupon.objects.get(id=cId)
            coupon.couponCode = couponCode
            coupon.validFrom = validFrom
            coupon.validTo = validTo
            coupon.discountType = discountType
            coupon.discountValue = discountValue
            coupon.fixedDiscountValue = fixedDiscountValue
            coupon.minPurchaseAmount = minPurchaseAmount
            coupon.maxDiscountAmount = maxDiscountAmount
            coupon.usageLimit = usageLimit

            coupon.applicableProducts.set(applicableProducts)
            coupon.applicableBrand.set(applicableBrand)
            coupon.applicableCategory.set(applicableCategory)

            coupon.save()
        except Coupon.DoesNotExist:
            return HttpResponse("Coupon not found", status=404)

        return redirect('addCoupon')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    products = Products.objects.all()
    coupon = Coupon.objects.get(id=cId)

    context = {
        'categories': categories,
        'brands': brands,
        'products': products,
        'coupon': coupon,
    }
    return render(request, 'editCoupon.html', context)
@never_cache
def deleteCoupon(request,cId):
    coupon = Coupon.objects.get(id=cId)
    coupon.delete()
    return redirect('addCoupon')

@never_cache
def couponDetail(request,cId):
    coupon = Coupon.objects.get(id=cId)
    context = {
        'coupon':coupon
    }
    return render(request,'couponDetails.html',context)