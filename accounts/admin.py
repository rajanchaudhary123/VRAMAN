from django.contrib import admin
from . models import User
from . models import UserProfile
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display=('username','first_name','last_name','email','phone_number','role','is_active')
    ordering = ('-date_joined',)
    filter_horizontal= ()
    list_filter= ()
    fieldsets= ()


admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile)