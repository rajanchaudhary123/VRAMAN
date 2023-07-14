import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.db.models.fields.related import ForeignKey, OneToOneField
from django.core.validators import RegexValidator


from django.contrib.gis.db import models as gismodels
from django.contrib.gis.geos import Point
from django.forms import ValidationError
 
 
 
class UserManager(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None,):
        if not email:
            raise ValueError('User must have email address')
        
        if not username:
            raise ValueError('User must enter username')
        
        user=self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
            

        )
        user.set_password(password) #SAR256#format
        user.save(using=self._db)
        return user
    

    def create_superuser(self, first_name, last_name, username, email, password=None):
        user = self.create_user(
            email = self.normalize_email(email),
            username = username,
            password = password,
            first_name = first_name,
            last_name = last_name,
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):

    VENDOR = 1
    CUSTOMER = 2  

    ROLE_CHOICE = (
        (VENDOR, 'Vendor'),
        (CUSTOMER, 'Customer'),
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[phone_regex]
    )
    interest = models.CharField(max_length=50, null=True )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICE, blank=True, null=True)

    # required fields
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = UserManager()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email
    def clean(self):
        super().clean()
        if self.email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, self.email):
                raise ValidationError("Invalid email address.")

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
    def get_role(self):
        if self.role == 1:
            user_role = 'Vendor'
        elif self.role == 2:
            user_role = 'Customer'
        return user_role

    def clean(self):
        super().clean()
        if self.phone_number:
            self.phone_number = self.phone_number.strip()
class UserProfile(models.Model):
    user = OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='users/profile_pictures', blank=True, null=True)
    cover_photo = models.ImageField(upload_to='users/cover_photos', blank=True, null=True)
    address = models.CharField(max_length=250, blank=True, null=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        max_length=17,
        blank=True,
        validators=[phone_regex]
    )
    
    country = models.CharField(max_length=15, blank=True, null=True)
    state = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=15, blank=True, null=True)
    pin_code = models.CharField(max_length=6, blank=True, null=True)
    latitude = models.CharField(max_length=20, blank=True, null=True)
    longitude = models.CharField(max_length=20, blank=True, null=True)

    location = gismodels.PointField(blank=True, null=True, srid=4326)
    interest_first = models.CharField(max_length=15, blank=True, null=True)
    interest_second = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    #def full_address(self):
       # return f'{self.address_line_1}, {self.address_line_2}'



    def __str__(self):
        return self.user.email
      #overriding the save function
    def save(self, *args, **kwargs):
        if self.latitude and self.longitude:
            self.location = Point(float(self.longitude), float(self.latitude))
            return super(UserProfile, self).save(*args, **kwargs)
        return super(UserProfile, self).save(*args, **kwargs)


