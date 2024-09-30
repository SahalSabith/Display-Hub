from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
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
import razorpay
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from discounts.models import BrandOffer,ProductOffer
from userProfile.models import Wallet,Transaction
from django.db import transaction
# Create your views here.

RAZOR_KEY_ID = config('RAZOR_KEY_ID')
RAZOR_KEY_SECRET = config('RAZOR_KEY_SECRET')

@never_cache
@login_required(login_url='/signIn')
def cart(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(userId=user)
    cartItems = CartItem.objects.filter(cartId=cart).order_by('-id')
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

    try:
        variant = Varients.objects.get(id=variant_id)
        if variant.stock >= quantity:
            cart, _ = Cart.objects.get_or_create(userId=request.user)
            cart_item, created = CartItem.objects.get_or_create(
                productId=variant.product,
                varientId=variant,
                cartId=cart,
                price=price,
                defaults={'quantity': 0}  # Initialize quantity to 0
            )
            cart_item.quantity += quantity  # Add the new quantity
            cart_item.save()
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
    cartUser = get_object_or_404(Cart,userId=request.user)
    cartItem = CartItem.objects.get(cartId=cartUser,id=cId)
    cartItem.delete()
    return redirect('cart')

@never_cache
def products(request):
    # Get the search query
    query = request.GET.get('q')

    # Get all products
    productsList = Products.objects.all()

    # Filter products based on search query
    if query:
        productsList = productsList.filter(name__icontains=query)  # Case-insensitive search on product name

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

    # Filter size, refresh rates, and categories (with counts)
    sizes = Size.objects.values('size').annotate(count=Count('size')).order_by('size')
    refreshRates = RefreshRate.objects.values('refreshRate').annotate(count=Count('refreshRate')).order_by('refreshRate')
    categories = Products.objects.values('category').annotate(count=Count('category')).order_by('category')

    # Pagination
    paginator = Paginator(productsList, 6)  # 6 products per page
    page_number = request.GET.get('page')

    try:
        products_final = paginator.get_page(page_number)
    except:
        products_final = paginator.page(paginator.num_pages)

    # Context for template
    context = {
        'products': products_final,
        'categories': Category.objects.all(),
        'sort': sort,
        'sizes': sizes,
        'category': categories,
        'refresh_rates': refreshRates,
        'query': query,  # Pass the search query to the template
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
        try:
            offer = ProductOffer.objects.get(applicableProducts=pId)
            offerValue = offer.discountValue

            offerAmount = (productAmount * offerValue) / 100
            finalAmount = productAmount - offerAmount
            print('offer available')
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
            print("No offer")
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
                    try:
                        offer = ProductOffer.objects.get(applicableProducts=pId)
                        offerValue = offer.discountValue

                        offerAmount = (productAmount * offerValue) / 100
                        finalAmount = productAmount - offerAmount

                        print("Offer Available")
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
                        print("No Offer")
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
    order = Order.objects.get(id=oId)
    orderPk = order.pk

    orderItems = OrderItem.objects.filter(orderItemId=order)

    context = {
        'order': order,
        'orders': orderItems,
        'orderPk':orderPk
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
                wallet, created = Wallet.objects.get_or_create(userId=user)  # Unpack the tuple
                orderAmount = order.totalPrice

                wallet.balance = wallet.balance+orderAmount
                wallet.save()

                transactions = Transaction.objects.create(walletId=wallet, TransactionType='refund', amount=orderAmount)
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

@never_cache
@login_required(login_url='/signIn')
def checkOut(request):
    userId = request.user
    addresses = Address.objects.filter(userId=userId)
    try:
        cart = Cart.objects.get(userId=userId)
    except ObjectDoesNotExist:
        return redirect('cart')
    cart_items = CartItem.objects.filter(cartId=cart).order_by('-id')
    coupon = Coupon.objects.all()

    for coupon in coupon:
        if coupon.validTo < datetime.now().date():
            coupon.status = False
            coupon.save()

    coupons = Coupon.objects.filter(status=True)

    if not cart_items.exists():
        messages.error(request, 'Please add items to the cart')
        return redirect('cart')

    if request.method == 'POST':
        try:
            # Get address and payment information
            data = json.loads(request.body)
            addressId = data.get('selectedAddress')
            address = Address.objects.get(id=addressId)
            payment_method = data.get('selectedPayment')
            final_order_price = data.get('finalOrderPrice')

            # Razorpay payment integration for 'internetBanking'
            razorpay_order = None
            if payment_method == 'internetBanking':
                client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
                razorpay_order = client.order.create(
                    {"amount": int(final_order_price) * 100, "currency": "INR", "payment_capture": "1"}
                )

            if not payment_method:
                messages.error(request, 'Please select a payment method.')
                return JsonResponse({'message': 'No Payment Selected', 'status': 'error'}, status=400)

            # Generate a random order number
            characters = string.ascii_letters + string.digits
            order_number = ''.join(random.choice(characters) for _ in range(10))

            if payment_method == 'wallet':
                wallet = Wallet.objects.get(userId=userId)
                if wallet.balance < float(final_order_price):
                    return JsonResponse({'message': 'Insufficient wallet balance', 'status': 'error'}, status=400)
                order_status = 'PENDING'  # Set to PENDING, will be updated after confirmation
            elif payment_method == 'internetBanking':
                order_status = 'FAILURE'
            else:
                order_status = 'dispatched'

            order = Order.objects.create(
                userId=userId,
                addressId=address,
                paymentMethod=payment_method,
                orderNo=order_number,
                totalPrice=final_order_price,
                orderStatus=order_status,
                provider_order_id=razorpay_order['id'] if razorpay_order else None 
            )


            # Create order items and update stock
            for item in cart_items:
                product = Products.objects.get(id=item.productId.id)
                variant = Varients.objects.get(id=item.varientId.id)
                OrderItem.objects.create(
                    orderItemId=order,
                    productId=product,
                    varientId=variant,
                    quantity=item.quantity,
                    totalPrice=item.cartItemTotal()
                )
                variant.stock -= item.quantity
                variant.save()

            # Clear cart after order is placed
            cart_items.delete()
            cart.delete()

            # Prepare data for Razorpay payment page if payment method is Razorpay
            if payment_method == 'internetBanking':
                response_data = {
                    'message': 'Order Successful',
                    'status': 'success',
                    'selectedAddress':address.phone,
                    'razorpay_order_id': razorpay_order['id'],
                    'razorpay_key': RAZOR_KEY_ID,
                    'callback_url': 'http://127.0.0.1:8000/razorpay/callback/',
                    'order_name': order_number,
                    'final_order_price': final_order_price
                }
                return JsonResponse(response_data, status=200)

            # Return success for non-Razorpay payment method
            return JsonResponse({'message': 'Order Successful', 'status': 'success'}, status=200)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)

    context = {'products': cart_items, 'addresses': addresses, 'cart': cart, 'coupons': coupons}
    return render(request, 'checkout.html', context)

@login_required
def get_wallet_balance(request):
    wallet, created = Wallet.objects.get_or_create(userId=request.user)
    return JsonResponse({'balance': wallet.balance})

@require_POST
@login_required
@transaction.atomic
def process_wallet_payment(request):
    data = json.loads(request.body)
    final_order_price = float(data.get('finalOrderPrice'))
    
    wallet = Wallet.objects.get(userId=request.user)
    
    if wallet.balance < final_order_price:
        return JsonResponse({'status': 'error', 'message': 'Insufficient balance'}, status=400)
    
    # Deduct the amount from the wallet
    wallet.balance -= final_order_price
    wallet.save()
    
    # Create a transaction record
    Transaction.objects.create(
        walletId=wallet,
        transactionType='addMoney',
        amount=-final_order_price  # Negative amount for deduction
    )
    # Update the order status
    order = Order.objects.filter(userId=request.user).latest('orderedAt')
    order.orderStatus = 'dispatched'
    order.save()
    
    return JsonResponse({'status': 'success', 'message': 'Payment processed successfully'})


@csrf_exempt
def razorpay_callback(request):
    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))
        try:
            client.utility.verify_payment_signature(response_data)
            return True
        except:
            return False

    if request.method == "POST":
        if "razorpay_signature" in request.POST:
            # Extract Razorpay details from POST request
            payment_id = request.POST.get("razorpay_payment_id", "")
            provider_order_id = request.POST.get("razorpay_order_id", "")
            signature_id = request.POST.get("razorpay_signature", "")

            # Fetch the corresponding order in your system
            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.signature_id = signature_id

            # Verify the signature
            if verify_signature(request.POST):
                # Signature is valid, mark payment as successful
                order.order_status = "SUCCESS"
                order.save()
                return render(request, "callback.html", context={"status": "success"})
            else:
                # Invalid signature, mark payment as failed
                order.order_status = "FAILURE"
                order.save()
                return render(request, "callback.html", context={"status": "failure"})
        else:
            # Handle Razorpay error response
            error_metadata = json.loads(request.POST.get("error[metadata]"))
            payment_id = error_metadata.get("payment_id", "")
            provider_order_id = error_metadata.get("order_id", "")

            # Fetch the corresponding order
            order = Order.objects.get(provider_order_id=provider_order_id)
            order.payment_id = payment_id
            order.order_status = "FAILURE"
            order.save()

            return render(request, "callback.html", context={"status": "failure"})

    return render(request, "callback.html", context={"status": "error"})