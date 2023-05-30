from django.shortcuts import get_object_or_404, render , redirect
from vendor.models import  Vendor
from menu.models import Category, PackageItem
from django.db.models import Prefetch
from .forms import ReviewForm
from django.contrib import messages
from .models import ReviewRating
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.views import check_role_customer
from django.http import HttpResponse,JsonResponse
from .models import Cart
from .context_processors import get_cart_counter

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
        'packageitems',
         queryset =PackageItem.objects.filter(is_available=True)
        )
    )

    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None
    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items': cart_items,
    }

    return render(request, 'marketplace/vendor_detail.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def submit_review(request, vendor_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, vendor__id =vendor_id)
            form = ReviewForm(request.POST,instance=reviews)
            form.save()
            messages.success(request,"Review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.vendor_id = vendor_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)


       
#in video139
def add_to_cart(request, package_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
           # Check if the package item exists
           try:
               packageitem=PackageItem.objects.get(id=package_id)
                # Check if the user has already added that package to the cart
               try:
                    chkCart = Cart.objects.get(user=request.user, packageitem=packageitem)
                    # decrease the cart quantity
                    chkCart.quantity += 1
                    chkCart.save()
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity','cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
                
               except:
                    chkCart = Cart.objects.create(user=request.user, packageitem=packageitem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the package to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
               
           
           except:
                return JsonResponse({'status': 'Failed', 'message': 'package doesnot exist'})
               
        else:
          return JsonResponse({'status': 'Failed', 'message': 'Please invalid'})
        

    else: 
      return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    
    

def decrease_cart(request, package_id):
 
   if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
           # Check if the package item exists
           try:
               packageitem=PackageItem.objects.get(id=package_id)
                # Check if the user has already added that package to the cart
               try:
                    chkCart = Cart.objects.get(user=request.user, packageitem=packageitem)
                    if chkCart.quantity > 1:
                    # decrease the cart quantity
                     chkCart.quantity -= 1
                     chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({'status': 'Success','cart_counter': get_cart_counter(request), 'qty': chkCart.quantity})
                
               except:
                    return JsonResponse({'status': 'Failed', 'message': 'You dont have this package in cart!!'})
               
           
           except:
                return JsonResponse({'status': 'Failed', 'message': 'package doesnot exist'})
               
        else:
          return JsonResponse({'status': 'Failed', 'message': 'Request invalid'})
        

   else: 
      return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
        