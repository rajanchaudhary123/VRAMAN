from django.shortcuts import get_object_or_404, render , redirect
from vendor.models import  Vendor
from menu.models import Category, PackageItem
from django.db.models import Prefetch
from .forms import ReviewForm
from django.contrib import messages
from .models import ReviewRating
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.views import check_role_customer
from django.http import HttpResponse

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

    context = {
        'vendor':vendor,
        'categories':categories,
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
    return HttpResponse('testing')
