from django.shortcuts import get_object_or_404, render , redirect
from accounts.models import UserProfile
from django.db.models import Avg, Count
from vendor.models import  Vendor
from vendor.models import  Vendor, OpeningHour
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
from datetime import date, datetime
from orders.models import OrderedPackage


#import for collaborative recommendation 
from .models import CollaborativeRecommendation

from accounts.models import User



def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    package = PackageItem.objects.filter(is_available=True)
    vendor_count = vendors.count()
    package_count = package.count()
    context = {
        'vendors': vendors,
        'vendor_count': vendor_count,
        'package_count':package_count,
    }
    return render(request, 'marketplace/listings.html', context)

def vendor_detail(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug=vendor_slug)
    reviews = ReviewRating.objects.filter(vendor=vendor.id, status=True).aggregate(average=Avg('rating'))
    avg1 = reviews['average'] or 0
    reviewcount = ReviewRating.objects.filter(vendor=vendor.id, status=True).aggregate(count=Count('id'))
    count = reviewcount['count'] or 0
    print(count)

    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
        'packageitems',
         queryset =PackageItem.objects.filter(is_available=True)
        )
    )
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day', '-from_hour')

    #check current day opening hour
    today_date = date.today()
    today = today_date.isoweekday()
    
    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day=today)
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    reviewvendor = ReviewRating.objects.filter(vendor = vendor.id, status=True)
    context = {
        'vendor':vendor,
        'categories':categories,
        'cart_items': cart_items,
        'opening_hours':opening_hours,
        'current_opening_hours':current_opening_hours,
        'reviewvendor':reviewvendor,
        'avg1': avg1,
        'count' : count,
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
@login_required(login_url='login')
@user_passes_test(check_role_customer)
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
                    return JsonResponse({'status': 'Success', 'message': 'Increased the wishlist quantity','cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
                
               except:
                    chkCart = Cart.objects.create(user=request.user, packageitem=packageitem, quantity=1)
                    return JsonResponse({'status': 'Success', 'message': 'Added the package to the wishlist', 'cart_counter': get_cart_counter(request), 'qty': chkCart.quantity,'cart_amount':get_cart_amounts(request)})
               
           
           except:
                return JsonResponse({'status': 'Failed', 'message': 'package doesnot exist'})
               
        else:
          return JsonResponse({'status': 'Failed', 'message': 'Please invalid'})
        

    else: 
      return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})
    
    
@login_required(login_url='login')
@user_passes_test(check_role_customer)
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
                    return JsonResponse({'status': 'Failed', 'message': 'You dont have this package in wishlist!!'})
               
           
           except:
                return JsonResponse({'status': 'Failed', 'message': 'package doesnot exist'})
               
        else:
          return JsonResponse({'status': 'Failed', 'message': 'Request invalid'})
        

   else: 
      return JsonResponse({'status': 'login_required', 'message': 'Please login to continue'})


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_at')
    context = {
        'cart_items' : cart_items,
    }
    return render(request,'marketplace/cart.html', context)
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def delete_cart(request, cart_id):
    if request.user.is_authenticated:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            try:
                #check if the cart item exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({'status': 'Success','message':'Wishlist item has been deleted!','cart_counter': get_cart_counter(request),'cart_amount':get_cart_amounts(request)})
            except:
                return JsonResponse({'status': 'Failed', 'message': 'You dont have this package in wishlist!!'})
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
    
    #Search package
def search_package(request):
   

        
        
        keyword = request.GET['keyword']
        
        # get vendor ids that has the package item the user is looking for
        package_search = PackageItem.objects.filter(package_title__icontains=keyword, is_available=True)
        fetch_vendors_by_packageitems = PackageItem.objects.filter(package_title__icontains=keyword, is_available=True).values_list('vendor', flat=True)
        
        vendors = Vendor.objects.filter(Q(id__in=fetch_vendors_by_packageitems) | Q(vendor_name__icontains=keyword, is_approved=True, user__is_active=True)) #Q is used in case of or logic ie complex query
        
        vendor_count = vendors.count()
        package_count = package_search.count()
                #for location based work
       
        context = {
                'package_search' : package_search,
                'package_count':package_count,
                'vendor_count': vendor_count,
                
            
            }
        
        return render(request,'marketplace/listings.html',context)
    
def package_detail(request, package_id):
    package = PackageItem.objects.filter(id=package_id)
    print(package_id)
    reviews = ReviewRatingPackage.objects.filter(package=package_id, status=True).aggregate(average=Avg('rating'))
    avg = reviews['average'] or 0
    print(avg)
    reviewcount1 = ReviewRatingPackage.objects.filter(package=package_id, status=True).aggregate(count1=Count('id'))
    count1 = reviewcount1['count1'] or 0
    print(count1)

    if request.user.is_authenticated:
        try:
            orderpackage = OrderedPackage.objects.filter(user=request.user, id=package_id).exists()
            print(orderpackage)
        except OrderedPackage.DoesNotExist:
            orderpackage = None
    else:
        orderpackage = None

    # Get the reviews
    reviewpackage = ReviewRatingPackage.objects.filter(package=package_id, status=True)
    print(reviewpackage)

    context = {
        'package': package,
        'orderpackage': orderpackage,
        'reviewpackage': reviewpackage,
        'reviews': reviews,
        'avg': avg,
        'count1':count1,
    }

    return render(request, 'marketplace/package_detail.html', context)
   
    return render(request, 'marketplace/package_detail.html',context)


#checkout
@login_required(login_url='login')
@user_passes_test(check_role_customer)
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



##collaborative filtering start
def recommend_packages(request):
    # Collaborative Filtering
   

    # # Get the user's cart items
    user_cart = Cart.objects.filter(user=request.user)
    user_cart_items = user_cart.values_list('packageitem__id', flat=True)
   

    # Find other users who have similar cart items
    similar_users = Cart.objects.filter(packageitem__in=user_cart_items).exclude(user=request.user)
    #similar_users_cart_items = similar_users.values_list('packageitem__id', flat=True)

    # Find the packages that are in the similar users' carts but not in the current user's cart
    #recommended_packages_cf =  PackageItem.objects.filter(id__in=similar_users_cart_items)[:8]
    # Save the collaborative recommendations for the user
    collaborative_recommendation, created = CollaborativeRecommendation.objects.get_or_create(user=request.user)
    

    similar_users_cart_items = Cart.objects.filter(user__in=similar_users.values_list('user')).exclude(user=request.user)
    recommended_packages_cf = PackageItem.objects.filter(cart__in=similar_users_cart_items).distinct()[:8]

    collaborative_recommendation.recommended_packages.set(recommended_packages_cf)
    context = {
        # 'user_cart':  user_cart,
        # 'user_cart_items ': user_cart_items ,
        'recommended_packages_cf': recommended_packages_cf,
        # Add other context variables
         'similar_users' : similar_users,
         'similar_users_cart_items' :  similar_users_cart_items
    }

    return render(request, 'home.html', context)

    # return render(request,'recommendation.html',context)
#collaborative filtering end


#category == interest start
def render_matching_packages(request):
    user = User.objects.get(pk=request.user.pk)

    # Retrieve the user's interest
    user_interest = user.interest

    # Retrieve the packages whose category matches the user's interest
    matching_packages = PackageItem.objects.filter(category__name=user_interest)


    context = {
        'matching_packages': matching_packages,
    }

    return render(request, 'matching_packages.html', context)




#category == interest enf