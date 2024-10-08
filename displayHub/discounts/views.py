from django.shortcuts import render, redirect,HttpResponse
from .models import Coupon
from django.views.decorators.cache import never_cache
from .models import Coupon,CouponUsage
from django.http import JsonResponse
import json
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import ProductOffer,BrandOffer
from adminManagements.models import Brand,Products
from django.contrib import messages
from django.utils import timezone

@never_cache
def addCoupon(request):
    if request.method == 'POST':
        couponCode = request.POST.get('couponCode')
        validTo = request.POST.get('validTo')
        discountValue = request.POST.get('discountValue')
        minPurchaseAmount = request.POST.get('minPurchaseAmount')
        maxPurchaseAmount = request.POST.get('maxPurchaseAmount')

        newCoupon = Coupon.objects.create(
            couponCode=couponCode,
            validTo=validTo,
            discountValue=discountValue,
            minPurchaseAmount=minPurchaseAmount,
            maxPurchaseAmount=maxPurchaseAmount
        )

        return redirect('addCoupon')
    
    coupons = Coupon.objects.all().order_by('-id')

    for coupon in coupons:
        if coupon.validTo < datetime.now().date():
            coupon.status = False
            coupon.save()

    context = {
        'coupon': coupons
    }

    return render(request, 'couponManagement.html', context)

@never_cache
def editCoupon(request, cId):
    if request.method == 'POST':
        couponCode = request.POST.get('couponCode')
        validTo = request.POST.get('validTo')
        discountValue = request.POST.get('discountValue')
        minPurchaseAmount = request.POST.get('minPurchaseAmount')
        maxPurchaseAmount = request.POST.get('maxPurchaseAmount')

        try:
            coupon = Coupon.objects.get(id=cId)
            coupon.couponCode = couponCode
            coupon.validTo = validTo
            coupon.discountValue = discountValue
            coupon.minPurchaseAmount = minPurchaseAmount
            coupon.maxPurchaseAmount = maxPurchaseAmount
            coupon.save()
        except Coupon.DoesNotExist:
            return HttpResponse("Coupon not found", status=404)

        return redirect('addCoupon')
    
    coupon = Coupon.objects.get(id=cId)

    context = {
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

@never_cache
def applyCoupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon_code = data.get('couponCode')
            total_amount = float(data.get('totalAmount', 0))
            
            coupon = Coupon.objects.get(couponCode__iexact=coupon_code, status=True)
            current_date = timezone.now().date()
            
            # Check if coupon is valid
            if not (coupon.validFrom <= current_date <= coupon.validTo):
                return JsonResponse({'message': 'Coupon has expired', 'status': 'error'}, status=400)
            
            # Check purchase amount limits
            if total_amount < coupon.minPurchaseAmount or total_amount > coupon.maxPurchaseAmount:
                return JsonResponse({'message': 'Purchase amount is not within coupon limits', 'status': 'error'}, status=400)
            
            # Check if user has already used this coupon
            if CouponUsage.objects.filter(coupon=coupon, user=request.user).exists():
                return JsonResponse({'message': 'You have already used this coupon', 'status': 'error'}, status=400)
            
            # Calculate discount
            discount_amount = min(total_amount * coupon.discountValue / 100, coupon.maxPurchaseAmount - coupon.minPurchaseAmount)
            final_total = total_amount - discount_amount
            
            # Record coupon usage
            CouponUsage.objects.create(coupon=coupon, user=request.user)
            
            # Save coupon info in session for persistence
            request.session['applied_coupon'] = {
                'code': coupon.couponCode,
                'discount_amount': discount_amount,
                'final_total': final_total
            }
            
            return JsonResponse({
                'message': 'Coupon applied successfully',
                'status': 'success',
                'discountAmount': discount_amount,
                'finalTotal': final_total
            }, status=200)
            
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'Invalid coupon code', 'status': 'error'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON', 'status': 'error'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e), 'status': 'error'}, status=500)
    
    return JsonResponse({'message': 'Invalid request', 'status': 'error'}, status=400)

@never_cache
def offers(request):
    productOffer = ProductOffer.objects.all().order_by('-id')
    brandOffer = BrandOffer.objects.all().order_by('-id')
    brands = Brand.objects.all().order_by('-id')
    products = Products.objects.all().order_by('-id')
    context = {
        'productOffers':productOffer,
        'brandOffers':brandOffer,
        'brands':brands,
        'products':products
    }
    return render(request,'offers.html',context)

from django.shortcuts import render

@never_cache
def addBrandOffer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        discountValue = request.POST.get('discountValue')
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')
        applicableBrandId = request.POST.get('applicableBrand')
        
        applicableBrand = Brand.objects.get(id=applicableBrandId)

        newOffer = BrandOffer.objects.create(
            name=name,
            discountValue=discountValue,
            startDate=startDate,
            endDate=endDate,
            applicableBrand=applicableBrand
        )
        return redirect('offers')
    return redirect('offers')

@never_cache
def addProductOffer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        discountValue = request.POST.get('discountValue')
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')
        applicableProductId = request.POST.get('applicableProducts')
        
        applicableProduct = Products.objects.get(id=applicableProductId)

        newOffer = ProductOffer.objects.create(
            name=name,
            discountValue=discountValue,
            startDate=startDate,
            endDate=endDate,
            applicableProducts=applicableProduct
        )
        return redirect('offers')
    return redirect('offers')

@never_cache
def removeOffer(request, oId):
    try:
        product_offer = ProductOffer.objects.get(id=oId)
        product_offer.delete()
    except ProductOffer.DoesNotExist:
        try:
            brand_offer = BrandOffer.objects.get(id=oId)
            brand_offer.delete()
        except BrandOffer.DoesNotExist:
            messages.error(request, "Offer not found.")
            return redirect('offers')
    
    return redirect('offers')
