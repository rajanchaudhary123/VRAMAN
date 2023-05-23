from django.shortcuts import render,redirect
from django.http import HttpResponse
from accounts.utils import detectUser,send_verification_email

from vendor.forms import VendorForm
from .forms import UserForm
from .models import User,UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required,user_passes_test

from django.core.exceptions import PermissionDenied

# Restrict the vendor from accessing the customer page
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer from accessing the vendor page
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied



def registerUser(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        #print(request.POST)
        form = UserForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER


            

            #last_name = form.cleaned_data['last_name']
            #username = form.cleaned_data['username']
            #email = form.cleaned_data['email']
            #interest = form.cleaned_data['interest']
            #password = form.cleaned_data['password']
            #user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, interest=interest, password=password)
            #user.role = User.CUSTOMER
            user.save()

            # send verification email
            #mail_subject = 'Please activate your account'
            #email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user)
            messages.success(request, 'Your account has been registered sucessfully!')
            return redirect('registerUser')
             




            messages.success(request, "your account has been registered successfully!")
            return redirect('registerUser')
        else:
            print('invalid form')
            print(form.errors)

    else:
        form = UserForm()
    context = {
        'form': form,
    }
    return render(request,'accounts/registerUser.html',context)


# Register Vendor

def registerVendor(request):
   if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('myAccount')
   elif request.method == 'POST':
       # store the data and create the user
      form = UserForm(request.POST)
      v_form = VendorForm(request.POST,request.FILES)
      if form.is_valid() and v_form.is_valid:
          first_name = form.cleaned_data['first_name']
          last_name = form.cleaned_data['last_name']
          username = form.cleaned_data['username']
          email = form.cleaned_data['email']
          password = form.cleaned_data['password']
          interest = form.cleaned_data['interest']
          user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, email=email, password=password)
          user.role= User.VENDOR
          user.save()
          vendor = v_form.save(commit=False)
          vendor.user = user
          user_profile = UserProfile.objects.get(user=user)
          vendor.user_profile = user_profile
          vendor.save()

          # send verification email
          send_verification_email(request, user)

          messages.success(request,"your account has been registered successfully! Please wait for approval.")
          return redirect('registerVendor')

      else:
          print('Invalid form')
          print(form.errors)
   else:
     form = UserForm()
     v_form = VendorForm()

   context = {
        'form': form,
        'v_form': v_form,
    }
   return render(request,'accounts/registerVendor.html',context)


def activate(request, uidb64, token):
    # activate the user by setting the is_active status true
    return

# login
def login(request):
    if request.user.is_authenticated:
        messages.warning(request, 'You are already logged in!')
        return redirect('dashboard')
    elif request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
     
    return render(request,'accounts/login.html')


#logout
def logout(request):
    auth.logout(request)
    messages.info(request, 'You are logged out.')
    return redirect('login')


#identify role vendor or customer
@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)


#dashboard customer
@login_required(login_url='login')
@user_passes_test(check_role_customer)
def custDashboard(request):
    return render(request,'accounts/custDashboard.html')



#vendor dashboard
@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request,'accounts/vendorDashboard.html')
  
    
    

    