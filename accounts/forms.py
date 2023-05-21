from django import forms
from .models import User

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