
from django import forms 
from .models import Category,PackageItem
from accounts.validators import allow_only_images_validator


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','description']

class PackageItemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),validators=[allow_only_images_validator],required=False)
    image2 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),validators=[allow_only_images_validator],required=False)
    image3 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),validators=[allow_only_images_validator],required=False)
    image4 = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),validators=[allow_only_images_validator],required=False)
    latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    class Meta:
        model = PackageItem
        fields = ['category', 'package_title', 'description','experiences_covered','inclusions','durations', 'price', 'image','image2','image3','image4','address','country','state','city','pin_code','latitude','longitude', 'is_available']

