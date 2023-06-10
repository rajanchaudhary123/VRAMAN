from django import forms 
from .models import ReviewRating,ReviewRatingPackage
from orders.models import Order

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']

class ReviewFormPackage(forms.ModelForm):
    class Meta:
        model = ReviewRatingPackage
        fields = ['subject','review','rating']




class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'phone', 'email', 'address', 'country', 'state', 'city', 'pin_code']