from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
from menu.models import PackageItem

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # ``D`` is a shortcut for ``Distance``
from django.contrib.gis.db.models.functions import Distance
from django.contrib.auth.decorators import login_required,user_passes_test

from marketplace.models import CollaborativeRecommendation
from marketplace.models  import Cart
  #for category based import
from accounts.models import User
from django import template
from accounts.views import check_role_customer
from django.db.models import Avg
from marketplace.views import ReviewRatingPackage


def get_or_set_current_location(request):
    if 'lat' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        return lng, lat
    elif  'lat' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        request.session['lat'] = lat
        request.session['lng'] = lng
        return lng, lat
    else:
        return None

@login_required(login_url='login')
def home(request):

   # start colaborative recommendation from marketplace's recommend_packages
    
   # Get the user's cart items
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
    

  #end of  colaborative recommendation from marketplace's recommend_packages


#   #start of for category==interest
    user = User.objects.get(email=request.user.email)
    user_interest = user.interest
    package_items = PackageItem.objects.filter(category__category_name=user_interest)



#   #end of  category==interest

    package=PackageItem.objects.filter(is_available=True)[:8]

   # Get all packages with their average ratings greater than 3.5
    packages_with_avg_ratings = PackageItem.objects.annotate(average_rating=Avg('reviewratingpackage__rating'))
    filtered_packages = packages_with_avg_ratings.filter(average_rating__gte=3.5)

    for package in filtered_packages:
        print(f"Package: {package},Package ID: {package.id}, Average Rating: {package.average_rating}")

# Sort the packages in descending order based on average ratings
    sorted_packages = filtered_packages.order_by('-average_rating')

    if get_or_set_current_location(request) is not None:
    

        pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
        vendors = Vendor.objects.filter(user_profile__location__distance_lte=(pnt, D(km=1000))
                ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")
            
        for v in vendors:
            v.kms = round(v.distance.km, 1)
    
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'is_customer': (request.user.role == 'Customer'),
        'vendors': vendors,
        'package': package,
         'recommended_packages_cf': recommended_packages_cf,
        'package_items': package_items,
        'sorted_packages': sorted_packages,
       
          
         
    }
    if request.user.is_authenticated:
        return render(request, 'home.html', context)
    else:
        return render(request, 'home.html')

