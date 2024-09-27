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
# Ensure the request is a POST request
    if request.method == 'POST':
        user = request.user
        
        # Retrieve session data
        session_data = request.session.get('product_data', None)
        if not session_data:
            messages.error(request, "No product data in session.")
            return JsonResponse({'error': "No product data in session."}, status=400)
        
        # Retrieve product variant info from session
        variant_id = session_data.get('variant_id')
        
        # Check if the variant exists in the database
        try:
            variant = Varients.objects.get(id=variant_id)
        except Varients.DoesNotExist:
            messages.error(request, "Selected product variant does not exist.")
            return JsonResponse({'error': "No product data in session."}, status=400)

        # Create or retrieve the wishlist item for the user
        Wishlist.objects.get_or_create(userId=user, varientId=variant)

        messages.success(request, "Product successfully added to wishlist.")
        return redirect('wishlist')  # Assuming 'wishlist' is the name of your wishlist page

    # If it's not a POST request, redirect to the product page
    return JsonResponse({'error': "No product data in session."}, status=405)

@never_cache
@login_required(login_url='/signIn')
def removeWishlsit(request,vId):
    if request.method == 'POST':
        user = request.user# Load JSON data from the request body
        variant_id = vId  # Get variant_id from the data
        
        try:
            wishlistItem = Wishlist.objects.get(varientId=variant_id, userId=user)
            wishlistItem.delete()
            messages.success(request, "Product successfully removed from wishlist.")
            return JsonResponse({'success': True}, status=200)
        except Wishlist.DoesNotExist:
            messages.error(request, "Selected product variant does not exist in your wishlist.")
            return JsonResponse({'error': "No product found in wishlist."}, status=404)
        
    # If it's not a POST request, return an error
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