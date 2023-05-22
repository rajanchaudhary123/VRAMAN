from django import forms
from .models import Vendor

'''Category= [
    ('adventure', 'Adventure'),
    ('vacation and chill', 'Vacation and Chill'),
    ('sight seeing', 'Sight seeing'),
    ('pilgrimage and peace', 'Pilgrimage and Peace'),
    ('trekking','Trekking'),
    ('hiking','Hiking'),
    ]'''

class VendorForm(forms.ModelForm):
   # interest= forms.CharField(label='Interest ?', widget=forms.Select(choices=Category))
  
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license',]  