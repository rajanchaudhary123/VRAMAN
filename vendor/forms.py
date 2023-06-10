from django import forms
from .models import Vendor, OpeningHour
from accounts.validators import allow_only_images_validator

'''Category= [
    ('adventure', 'Adventure'),
    ('vacation and chill', 'Vacation and Chill'),
    ('sight seeing', 'Sight seeing'),
    ('pilgrimage and peace', 'Pilgrimage and Peace'),
    ('trekking','Trekking'),
    ('hiking','Hiking'),
    ]'''

class VendorForm(forms.ModelForm):
    vendor_license = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),validators=[allow_only_images_validator])
   # interest= forms.CharField(label='Interest ?', widget=forms.Select(choices=Category))
  
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license',]  

class OpeningHourForm(forms.ModelForm):
    class Meta:
        model = OpeningHour
        fields = ['day', 'from_hour', 'to_hour', 'is_closed']

    