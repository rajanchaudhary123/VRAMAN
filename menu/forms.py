from django import forms 
from .models import Category,PackageItem
from accounts.validators import allow_only_images_validator


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category_name','description']

class PackageItemForm(forms.ModelForm):
    image = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info w-100'}),validators=[allow_only_images_validator])
    class Meta:
        model = PackageItem
        fields = ['category', 'package_title', 'description', 'price', 'image', 'is_available']