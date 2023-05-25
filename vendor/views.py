from django.shortcuts import get_object_or_404, render,redirect
from .forms import VendorForm
from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from .models import Vendor
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from accounts.views import check_role_vendor
from menu.models import Category, PackageItem
from menu.forms import CategoryForm ,PackageItemForm
from django.template.defaultfilters import slugify


def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

# Create your views here.
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance=vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Settings updated.')
            return redirect('vprofile')
        else:
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance = profile)
        vendor_form = VendorForm(instance=vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile':profile,
        'vendor': vendor,

    }
    return render (request,'vendor/vprofile.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories= Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request,'vendor/menu_builder.html',context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def packageitems_by_category(request,pk=None):
    vendor = vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    packageitems = PackageItem.objects.filter(vendor=vendor, category=category)
    context = {
        'packageitems': packageitems,
        'category': category,
    }
    return render(request,'vendor/packageitems_by_category.html',context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            
           # category.save() # here the category id will be generated
            category.slug = slugify(category_name) #+'-'+str(category.id) # chicken-15
            form.save()
            #category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)

    else:
        form = CategoryForm()
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)

    else:
        form = CategoryForm(instance=category)
    context = {
        'form': form,
        'category': category,
    }
    return render(request, 'vendor/edit_category.html', context)


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')

#using keyword package
@login_required(login_url='login')
@user_passes_test(check_role_vendor)

def add_package(request):
    if request.method == 'POST':
        form = PackageItemForm(request.POST, request.FILES)
        if form.is_valid():
            packagetitle = form.cleaned_data['package_title']
            package = form.save(commit=False)
            package.vendor = get_vendor(request)
            
           # category.save() # here the category id will be generated
            package.slug = slugify(packagetitle) #+'-'+str(category.id) # chicken-15
            form.save()
            #category.save()
            messages.success(request, 'Package added successfully!')
            return redirect('packageitems_by_category',package.category.id)
        else:
            print(form.errors)
    else:
     form= PackageItemForm()
     # modify this form
     form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context={
        'form':form
    }

    return render(request, 'vendor/add_package.html',context)



@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_package(request, pk=None):
    package = get_object_or_404(PackageItem, pk=pk)
    if request.method == 'POST':
        form = PackageItemForm(request.POST, request.FILES, instance=package)
        if form.is_valid():
            packagetitle = form.cleaned_data['package_title']
            package = form.save(commit=False)
            package.vendor = get_vendor(request)
            package.slug = slugify(packagetitle)
            form.save()
            messages.success(request, 'Package updated successfully!')
            return redirect('packageitems_by_category',package.category.id)
        else:
            print(form.errors)

    else:
        form = CategoryForm(instance=package)
        form.fields['category'].queryset = Category.objects.filter(vendor=get_vendor(request))

    context = {
        'form': form,
        'package': package,
    }
    return render(request, 'vendor/edit_package.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_package(request, pk=None):
    package = get_object_or_404(PackageItem, pk=pk)
    package.delete()
    messages.success(request, 'package has been deleted successfully!')
    return redirect('packageitems_by_category',package.category.id)