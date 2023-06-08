from django import forms 
from .models import ReviewRating,ReviewRatingPackage

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']

class ReviewFormPackage(forms.ModelForm):
    class Meta:
        model = ReviewRatingPackage
        fields = ['subject','review','rating']