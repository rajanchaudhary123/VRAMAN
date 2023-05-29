from django.shortcuts import render
from django.http import HttpResponse
from vendor.models import Vendor
from menu.models import PackageItem

def home(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    packages = PackageItem.objects.filter(is_available=True)[:8]
    print(vendors)
    context = {
        'vendors': vendors,
        'packages': packages,
    }
    return render(request,'home.html',context)