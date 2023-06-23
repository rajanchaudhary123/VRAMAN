from django.utils import timezone
import datetime
from django import forms 
from .models import ReviewRating,ReviewRatingPackage
from orders.models import Order

from django.contrib.admin.widgets import AdminDateWidget
from django.forms.fields import DateField

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']

class ReviewFormPackage(forms.ModelForm):
    class Meta:
        model = ReviewRatingPackage
        fields = ['subject','review','rating']




class OrderForm(forms.ModelForm):
    def validate_date(date):
      if date < timezone.now().date():
        raise forms.ValidationError("Date cannot be in the past")
      
    
      

    start_date=forms.DateField(widget = forms.SelectDateWidget(),validators=[validate_date])
    #end_date=forms.DateField(widget = forms.SelectDateWidget(),validators=[validate_date])
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'start_date','address', 'country', 'state', 'city', 'pin_code']