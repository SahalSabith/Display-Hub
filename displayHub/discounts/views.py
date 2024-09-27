from django.shortcuts import render, redirect,HttpResponse
from .models import Coupon
from django.views.decorators.cache import never_cache
from .models import Coupon
from django.http import JsonResponse
import json
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from .models import ProductOffer,BrandOffer
from adminManagements.models import Brand,Products
from django.contrib import messages

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
        currentDate = datetime.now().date()
        print(currentDate)
        try:
            couponCode = json.loads(request.body).get('couponCode')
            coupon = Coupon.objects.get(couponCode__iexact=couponCode)
            if coupon.validFrom <= currentDate <= coupon.validTo:
                responseData = {
                    'message': 'Coupon Applied',
                    'status': 'success',
                    'discountValue':coupon.discountValue,
                    'minPurchaseAmount':coupon.minPurchaseAmount,
                    'maxPurchaseAmount':coupon.maxPurchaseAmount
                }
                return JsonResponse(responseData, status=200)
            else:
                errorData = {
                'message': 'No Coupon Applied',
                'status': 'error',
                }
                return JsonResponse(errorData, status=400)
        except ObjectDoesNotExist:
            errorData = {
                'message': 'No Coupon Applied',
                'status': 'error',
            }
            return JsonResponse(errorData, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'message': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    
    return JsonResponse({'message': 'Invalid Request'}, status=400)

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
