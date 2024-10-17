from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404,HttpResponse
from adminManagements.models import Products,Brand,Category,Size,RefreshRate,Varients
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from . models import Cart,CartItem,Order,OrderItem
from django.db import IntegrityError
from django.urls import reverse
from userProfile.models import Address
import random
import string
from django.contrib import messages
from django.db.models import Count
from django.db import models
from django.db.models import Min
import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from discounts.models import Coupon
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from discounts.models import BrandOffer,ProductOffer
from userProfile.models import Wallet,Transaction
from django.utils import timezone
from django.db.models import Min, Count, Q
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
# Create your views here.

@never_cache
@login_required(login_url='/signIn')
def cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(userId=user)
    cartItems = CartItem.objects.filter(cartId=cart).order_by('-id')
    cart = Cart.objects.get(userId=user)
    cartItem = CartItem.objects.filter(cartId=cart).count()
    request.session['cartCount'] = cartItem
    context = {
        'items': cartItems
    }
    return render(request, 'cart.html', context)
@require_POST
@never_cache
@login_required(login_url='/signIn')
def updateQuantity(request):
    user = request.user
    data = json.loads(request.body)
    item_id = data.get('item_id')
    action = data.get('action')

    try:
        cart_item = CartItem.objects.get(id=item_id, cartId__userId=user)
        if action == 'increase':
            if cart_item.quantity < cart_item.varientId.stock:
                cart_item.quantity += 1
                cart_item.save()
                return JsonResponse({'success': True, 'new_quantity': cart_item.quantity})
            else:
                return JsonResponse({'success': False, 'error': 'Insufficient stock'})
        elif action == 'decrease':
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                return JsonResponse({'success': True, 'new_quantity': cart_item.quantity})
            else:
                cart_item.delete()
                cart = cart_item.cartId
                cart.delete()
                return JsonResponse({'success': True, 'new_quantity': 0, 'removed': True})
    except CartItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Item not found'})

    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required(login_url='/signIn')
@require_POST
def addToCart(request):
    data = json.loads(request.body)
    variant_id = data.get('variant_id')
    quantity = data.get('quantity', 1)
    price = data.get('price')
    user = request.user
    if user:
        None
    else:
        return JsonResponse({'success': False, 'message': 'Logi Please'})
    try:
        variant = Varients.objects.get(id=variant_id)
        if variant.stock >= quantity:
            cart, _ = Cart.objects.get_or_create(userId=user)
            cart_item, created = CartItem.objects.get_or_create(
                productId=variant.product,
                varientId=variant,
                cartId=cart,
                price=price,
                defaults={'quantity': 0}  # Initialize quantity to 0
            )
            cart_item.quantity += quantity  # Add the new quantity
            cart_item.save()

            cart = Cart.objects.get(userId=user)
            cartItems = CartItem.objects.filter(cartId=cart).count()
            request.session['cartCount'] = cartItems

            return JsonResponse({'success': True, 'message': 'Product added to cart'})
        else:
            return JsonResponse({'success': False, 'message': 'Not enough stock available'})
    except Varients.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product variant not found'})

@login_required
def checkCart(request, variant_id):
    try:
        variant = Varients.objects.get(id=variant_id)
        cart = Cart.objects.get(userId=request.user)
        in_cart = CartItem.objects.filter(cartId=cart, varientId=variant).exists()
        return JsonResponse({'inCart': in_cart})
    except (Varients.DoesNotExist, Cart.DoesNotExist):
        return JsonResponse({'inCart': False})

@never_cache
@login_required(login_url='/signIn')
def removeCart(request, cId):
    user = request.user
    cartUser = get_object_or_404(Cart,userId=user)
    cartItem = CartItem.objects.get(cartId=cartUser,id=cId)
    cartItem.delete()
    cart = Cart.objects.get(userId=user)
    cartItems = CartItem.objects.filter(cartId=cart).count()
    request.session['cartCount'] = cartItems
    return redirect('cart')

@never_cache
def products(request):
    # Get all products
    productsList = Products.objects.filter(status=True, category__status=True, brand__status=True)

    # Get the search query
    query = request.GET.get('q')
    if query:
        productsList = productsList.filter(name__icontains=query)

    # Filter by category
    category = request.GET.get('category')
    if category:
        productsList = productsList.filter(category__name=category)

    # Filter by size
    sizes = request.GET.getlist('size')
    if sizes:
        productsList = productsList.filter(varient__size__size__in=sizes)

    # Filter by refresh rate
    refresh_rates = request.GET.getlist('refresh_rate')
    if refresh_rates:
        productsList = productsList.filter(varient__refreshRate__refreshRate__in=refresh_rates)

    # Filter by price range
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 100000)
    if min_price and max_price:
        productsList = productsList.filter(varient__price__gte=min_price, varient__price__lte=max_price)

    # Sorting logic
    sort = request.GET.get('sort')
    productsList = productsList.annotate(min_price=Min('varient__price'))

    if sort == 'price_asc':
        productsList = productsList.order_by('min_price')
    elif sort == 'price_desc':
        productsList = productsList.order_by('-min_price')
    elif sort == 'new_arrivals':
        productsList = productsList.order_by('-createdAt')
    elif sort == 'az':
        productsList = productsList.order_by('name')
    elif sort == 'za':
        productsList = productsList.order_by('-name')

    # Get filter options with counts (calculated from all active products)
    all_active_products = Products.objects.filter(status=True, category__status=True, brand__status=True).distinct()

    sizes = Size.objects.annotate(
        count=Count('varients', filter=Q(varients__product__in=all_active_products))
    )
    refresh_rates = RefreshRate.objects.annotate(
        count=Count('varients', filter=Q(varients__product__in=all_active_products))
    )
    categories = Category.objects.filter(status=True).annotate(
        count=Count('brand', filter=Q(brand__in=all_active_products))
    )

    # Pagination
    paginator = Paginator(productsList.distinct(), 8)  # 6 products per page
    page_number = request.GET.get('page')
    products_final = paginator.get_page(page_number)

    context = {
        'products': products_final,
        'categories': categories,
        'sizes': sizes,
        'refresh_rates': refresh_rates,
        'sort': sort,
        'query': query,
        'selected_category': category,
        'selected_sizes': sizes,
        'selected_refresh_rates': refresh_rates,
        'min_price': min_price,
        'max_price': max_price,
    }

    return render(request, 'shop.html', context)

@never_cache
def productInfo(request, pId):
    product = get_object_or_404(Products, id=pId)
    
    first_variant = product.varient.first()
    varientSize = product.varient.values('size_id', 'size__size').distinct()
    varientRefreshRates = product.varient.values('refreshRate_id', 'refreshRate__refreshRate').distinct()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        productAmount = first_variant.price
        current_time = timezone.now()
        try:
            try:  
                offer = ProductOffer.objects.get(
                    applicableProducts=pId,
                    startDate__lte=current_time,
                    endDate__gte=current_time,
                    status=True
                    )
                offerValue = offer.discountValue
            except ObjectDoesNotExist:
                brand = first_variant.product.brand
                offer = BrandOffer.objects.get(
                    applicableBrand=brand,
                    startDate__lte=current_time,
                    endDate__gte=current_time,
                    status=True
                )
                offerValue = offer.discountValue

            offerAmount = (productAmount * offerValue) / 100
            finalAmount = productAmount - offerAmount

            productData = {
                'product': {
                    'name': product.name,
                    'offerStatus':True,
                    'resolution': product.resolution,
                    'images': [
                        product.image1.url if product.image1 else None,
                        product.image2.url if product.image2 else None,
                        product.image3.url if product.image3 else None,
                        product.image4.url if product.image4 else None
                    ],
                    'first_variant': {
                        'price': finalAmount,
                        'orginalAmount':productAmount,
                        'size': first_variant.size.size,
                        'refreshRate': first_variant.refreshRate.refreshRate,
                        'stock': first_variant.stock,
                    } if first_variant else None
                },
                'varientSize': list(varientSize),
                'varientRefreshRates': list(varientRefreshRates),
            }
        except ObjectDoesNotExist:
            productData = {
                'product': {
                    'name': product.name,
                    'offerStatus':False,
                    'resolution': product.resolution,
                    'images': [
                        product.image1.url if product.image1 else None,
                        product.image2.url if product.image2 else None,
                        product.image3.url if product.image3 else None,
                        product.image4.url if product.image4 else None
                    ],
                    'first_variant': {
                        'price': productAmount,
                        'size': first_variant.size.size,
                        'refreshRate': first_variant.refreshRate.refreshRate,
                        'stock': first_variant.stock,
                    } if first_variant else None
                },
                'varientSize': list(varientSize),
                'varientRefreshRates': list(varientRefreshRates),
            }
        return JsonResponse(productData)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            size = data.get('size')
            refreshRate = data.get('refreshRate')
            responseData = {}
            if size:
                refreshRatesForSize = Varients.objects.filter(
                    size_id=size,
                    product=product
                ).values('refreshRate_id', 'refreshRate__refreshRate').distinct()

                responseData['refreshRates'] = list(refreshRatesForSize)

            if refreshRate:
                sizesForRefreshRate = Varients.objects.filter(
                    refreshRate_id=refreshRate,
                    product=product
                ).values('size_id', 'size__size').distinct()

                responseData['size'] = list(sizesForRefreshRate)

            if size and refreshRate:
                selectedVarient = Varients.objects.filter(
                    size_id=size,
                    refreshRate_id=refreshRate,
                    product=product
                ).first()

                if selectedVarient:
                    productAmount= selectedVarient.price
                    currentTime = timezone.now()
                    try:
                        try:
                            current_time = timezone.now()
                            brand = selectedVarient.product.brand
                            offer = BrandOffer.objects.get(
                                applicableBrand=brand,
                                startDate__lte=current_time,
                                endDate__gte=current_time,
                                status=True
                                )
                            offerValue = offer.discountValue
                        except ObjectDoesNotExist:
                            offer = ProductOffer.objects.get(
                                applicableProducts=pId,
                                startDate__lte=current_time,
                                endDate__gte=current_time,
                                status=True
                                )
                            offerValue = offer.discountValue

                        offerAmount = (productAmount * offerValue) / 100
                        finalAmount = productAmount - offerAmount

                        responseData.update({
                            'price': finalAmount,
                            'offerStatus':True,
                            'size': selectedVarient.size.size,
                            'refreshRate': selectedVarient.refreshRate.refreshRate,
                            'stock': selectedVarient.stock,
                            'variantId': selectedVarient.id,
                            'orginalAmount':productAmount,
                        })
                        
                    except ObjectDoesNotExist:
                        responseData.update({
                            'price': productAmount,
                            'size': selectedVarient.size.size,
                            'refreshRate': selectedVarient.refreshRate.refreshRate,
                            'stock': selectedVarient.stock,
                            'variantId': selectedVarient.id,
                            'offerStatus':False,
                        })
                else:
                    responseData['error'] = 'No matching variant found.'

            return JsonResponse(responseData)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid request format'}, status=400)

    return render(request, 'productInfo.html',{'pId':pId})

@never_cache
@login_required(login_url='/signIn')
def orderDetails(request, oId):
    user = request.user
    order = get_object_or_404(Order, id=oId, userId=user)
    orderItems = OrderItem.objects.filter(orderItemId=order)
    
    if not orderItems:
        order.delete()
        return redirect('order')
    
    activeOrderItems = OrderItem.objects.filter(orderItemId=order, status=True)
    if not activeOrderItems.exists():
        order.orderStatus = 'canceled'
        order.cancelReason = "User canceled all items"
        order.save()

    # Add available addresses for the modal
    addresses = Address.objects.filter(userId=user)

    context = {
        'order': order,
        'orders': orderItems,
        'orderPk': order.pk,
        'addresses': addresses,  # Pass addresses to template
    }
    return render(request, 'orderDetails.html', context)


@require_POST
@never_cache
@login_required(login_url='/signIn')
def cancelOrder(request, oId):
    try:
        order = Order.objects.get(id=oId)
        if order.orderStatus not in ['canceled', 'delivered', 'refunded']:
            reason = request.POST.get('reason', '')
            if reason == 'other':
                other_reason = request.POST.get('other_reason', '')
                if other_reason:
                    reason = other_reason
                else:
                    return JsonResponse({'error': 'Please provide a reason for cancellation.'}, status=400)
                
            if order.paymentMethod == 'internetBanking':
                user = request.user
                wallet, created = Wallet.objects.get_or_create(userId=user)
                orderAmount = order.totalPrice

                wallet.balance = wallet.balance+orderAmount
                wallet.save()

                transactions = Transaction.objects.create(walletId=wallet, transactionType='refund', amount=orderAmount)
                transactions.save()

            order.cancelReason = reason
            order.orderStatus = 'canceled'
            order.save()

            return JsonResponse({'success': True})

    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order does not exist'}, status=404)
    except OrderItem.DoesNotExist:
        return JsonResponse({'error': 'Order item does not exist'}, status=404)

    return JsonResponse({'error': 'Order cannot be canceled'}, status=400)

@require_POST
def returnOrder(request,oId):
    try:
        order = Order.objects.get(id=oId)
        if order.orderStatus not in ['canceled', 'refunded','returned']:
            reason = request.POST.get('reason', '')
            if reason == 'other':
                other_reason = request.POST.get('other_reason', '')
                if other_reason:
                    reason = other_reason
                else:
                    return JsonResponse({'error': 'Please provide a reason for cancellation.'}, status=400)

            order.returnReason = reason
            order.orderStatus = 'returnRequested'
            order.save()

            return JsonResponse({'success': True})

    except Order.DoesNotExist:
        return JsonResponse({'error': 'Order does not exist'}, status=404)
    except OrderItem.DoesNotExist:
        return JsonResponse({'error': 'Order item does not exist'}, status=404)

    return JsonResponse({'error': 'Order cannot be canceled'}, status=400)

def downloadInvoice(request,oId):
    order = Order.objects.get(id=oId)
    orderItems = OrderItem.objects.filter(orderItemId=order)

    html = render_to_string('orderInvoice.html', {'order': order, 'orderItems': orderItems})

    # Create a BytesIO buffer to hold the PDF data
    buffer = BytesIO()

    # Create a PDF from the HTML string
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), buffer)

    # If PDF creation fails, return an error
    if pdf.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    # Return the PDF as a response
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{oId}.pdf"'
    return response

@never_cache
@csrf_exempt
def removeProduct(request, pId):
    if request.method == 'POST':
        try:
            order_item = OrderItem.objects.get(id=pId)
            
            order = order_item.orderItemId

            if order.paymentMethod == 'internetBanking':
                user = order.userId
                wallet, created = Wallet.objects.get_or_create(userId=user)
                itemAmount = order_item.totalPrice

                wallet.balance = wallet.balance+itemAmount
                wallet.save()

                transactions = Transaction.objects.create(walletId=wallet, transactionType='refund', amount=itemAmount)
                transactions.save()


            order.totalPrice -= order_item.totalPrice
            order.save()

            order_item.status = False
            order_item.save()

            return JsonResponse({'success': 'Order Item canceled, total price updated'}, status=200)
        except OrderItem.DoesNotExist:
            return JsonResponse({'error': 'Order item not found'}, status=404)
    return JsonResponse({'error': 'Invalid request method'}, status=400)
