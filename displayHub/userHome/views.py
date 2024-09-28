from django.shortcuts import render,redirect,HttpResponseRedirect
from adminManagements.models import Products
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from .models import Wishlist
from django.contrib import messages
from adminManagements.models import Products,Varients
from django.http import JsonResponse
import json
# Create your views here.
@never_cache
def home(request):
    products = Products.objects.filter(status=True)
    return render(request,'index.html',{'products':products})

@never_cache
def contact(request):

    return render(request,'contact.html')


@login_required(login_url='/signIn')
@never_cache
def wishlist(request):
    user = request.user
    wishlistItems = Wishlist.objects.filter(userId=user)
    return render(request,'wishlist.html',{'wishlist':wishlistItems})

@never_cache
@login_required(login_url='/signIn')
def addToWishlist(request):
    if request.method == 'POST':
        user = request.user
        
        session_data = request.session.get('product_data', None)
        if not session_data:
            messages.error(request, "No product data in session.")
            return JsonResponse({'error': "No product data in session."}, status=400)
        
        variant_id = session_data.get('variant_id')
        
        try:
            variant = Varients.objects.get(id=variant_id)
        except Varients.DoesNotExist:
            messages.error(request, "Selected product variant does not exist.")
            return JsonResponse({'error': "No product data in session."}, status=400)

        Wishlist.objects.get_or_create(userId=user, varientId=variant)
        if 'product_data' in request.session:
            print(session_data)
            del request.session['product_data']
            print('session cleared')

        messages.success(request, "Product successfully added to wishlist.")
        return redirect('wishlist')
    
    return JsonResponse({'error': "No product data in session."}, status=405)

@never_cache
@login_required(login_url='/signIn')
def removeWishlsit(request,vId):
    if request.method == 'POST':
        user = request.user
        variant_id = vId
        
        try:
            wishlistItem = Wishlist.objects.get(varientId=variant_id, userId=user)
            wishlistItem.delete()
            messages.success(request, "Product successfully removed from wishlist.")
            return JsonResponse({'success': True}, status=200)
        except Wishlist.DoesNotExist:
            messages.error(request, "Selected product variant does not exist in your wishlist.")
            return JsonResponse({'error': "No product found in wishlist."}, status=404)
        
    return JsonResponse({'error': "Invalid request method."}, status=405)

@never_cache
@login_required(login_url='/signIn')
def removeAllFromWishlist(request):
    if request.method == 'POST':
        user = request.user
        
        # Remove all items from the user's wishlist
        Wishlist.objects.filter(userId=user).delete()

        messages.success(request, "All items successfully removed from your wishlist.")
        return JsonResponse({'success': True}, status=200)

    # If it's not a POST request, return an error
    return JsonResponse({'error': "Invalid request method."}, status=405)