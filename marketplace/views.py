from django.shortcuts import get_object_or_404, render , redirect
from accounts.models import UserProfile

from vendor.models import  Vendor
from menu.models import Category, PackageItem
from django.db.models import Prefetch
from .forms import ReviewForm,ReviewFormPackage
from django.contrib import messages
from .models import ReviewRating,ReviewRatingPackage
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.views import check_role_customer
from django.http import HttpResponse,JsonResponse
from .models import Cart
from .context_processors import get_cart_counter, get_cart_amounts
from django.db.models import Q
#for location based work
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance
from .forms import OrderForm



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
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def submit_review_package(request, package_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            reviews = ReviewRatingPackage.objects.get(user__id=request.user.id, package__id =package_id)
            form = ReviewFormPackage(request.POST,instance=reviews)
            form.save()
            messages.success(request,"Review has been updated.")
            return redirect(url)
        except ReviewRatingPackage.DoesNotExist:
            form = ReviewFormPackage(request.POST)
            if form.is_valid():
                data = ReviewRatingPackage()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.package_id = package_id
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
                    return JsonResponse({'status': 'Success', 'message': 'Increased the cart quantity','cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                
               except:
                    chkCart = Cart.objects.create(user=request.user, packageitem=packageitem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the package to the cart', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
               
           
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
                    return JsonResponse({'status': 'Success','cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                
               except:
                    return JsonResponse({'status': 'Failed', 'message': 'You dont have this package in cart!!'})
               
           
           except:
                return JsonResponse({'status': 'Failed', 'message': 'package doesnot exist'})
               
        else:
          return JsonResponse({'status': 'Failed', 'message': 'Request invalid'})
        

   else: 
      return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})

@login_required(login_url = 'login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items' : cart_items,
    }
    return render(request,'marketplace/cart.html', context)

def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success','message':'Cart item has been deleted!','cart_counter': get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'You dont have this package in cart!!'})
    else:
        return JsonResponse({'status': 'Failed', 'message': 'Request invalid'})
    
def search(request):
    if not 'address' in request.GET:
      return redirect('marketplace')
    else:

        address = request.GET['address']
        latitude = request.GET['lat']
        longitude = request.GET['lng']
        radius = request.GET['radius']
        keyword = request.GET['keyword']
        
        # get vendor ids that has the food item the user is looking for
        fetch_vendors_by_packageitems = PackageItem.objects.filter(package_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_packageitems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)) #Q is used in case of or logic ie complex query
        
        #for location based work
        if latitude and longitude and radius:
            pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
            vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_packageitems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True),
                user_profile__location__distance_lte=(pnt, D(km=radius))
                ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
            for v in vendors:
                    v.kms = round(v.distance.km, 1)
        
        vendor_count = vendors.count()
        context = {
                'vendors': vendors,
                'vendor_count': vendor_count,
                 'source_location': address,
            
            }
        
        return render(request,'marketplace/listings.html',context)
    
def package_detail(request, package_id):
    package=PackageItem.objects.filter(id=package_id)
    context={
        'package':package,
    }
   
   
    return render(request, 'marketplace/package_detail.html',context)


#checkout
@login_required(login_url='login')
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    user_profile = UserProfile.objects.get(user=request.user)
    default_values = {
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': request.user.phone_number,
        'email': request.user.email,
        'address': user_profile.address,
        'country': user_profile.country,
        'state': user_profile.state,
        'city': user_profile.city,
        'pin_code': user_profile.pin_code,
    }
    form = OrderForm(initial=default_values)
    context = {
        'form':form,
        'cart_items':cart_items,
        
    }
    
    return render(request,'marketplace/checkout.html',context)



            