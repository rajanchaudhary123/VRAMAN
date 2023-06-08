from django import forms
from .models import User,UserProfile
from .validators import allow_only_images_validator
from django.core.validators import RegexValidator

Interest= [
    ('adventure', 'Adventure'),
    ('vacation and chill', 'Vacation and Chill'),
    ('sight seeing', 'Sight seeing'),
    ('pilgrimage and peace', 'Pilgrimage and Peace'),
    ('trekking','Trekking'),
    ('hiking','Hiking'),
    ]

class UserForm(forms.ModelForm):
    interest= forms.CharField(label='Interest ?', widget=forms.Select(choices=Interest))
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = {'first_name', 'last_name', 'username','email','password','interest'}

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                "password does not match!"
            )


class UserProfileForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Start typing...', 'required': 'required'}))
    profile_picture = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),validators=[allow_only_images_validator])
    cover_photo = forms.FileField(widget=forms.FileInput(attrs={'class': 'btn btn-info'}),validators=[allow_only_images_validator])
    
    # latitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    # longitude = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'cover_photo', 'address','country', 'state', 'city', 'pin_code', 'latitude', 'longitude']


    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            if field == 'latitude' or field == 'longitude':
                self.fields[field].widget.attrs['readonly'] = 'readonly' 

class UserInfoForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )

    phone_number = forms.CharField(validators=[phone_regex])
    class Meta:
        model = User
        fields = ['first_name','last_name','phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].error_messages = {'invalid': 'Invalid phone number format.'}