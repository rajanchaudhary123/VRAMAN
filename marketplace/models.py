from django.db import models
from accounts.models import User
from vendor.models import Vendor
from menu.models import PackageItem

# Create your models here.
class ReviewRating(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    review = models.TextField(max_length= 500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
class ReviewRatingPackage(models.Model):
    package = models.ForeignKey(PackageItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    subject = models.CharField(max_length=50, blank=True)
    review = models.TextField(max_length= 500,blank=True)
    rating = models.FloatField()
    ip = models.CharField(max_length=20, blank=True)
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject
    
#maybe we need to include booking  date here-abhishek video-138
        
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    packageitem = models.ForeignKey(PackageItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.user


class Tax(models.Model):
    tax_type = models.CharField(max_length=20, unique=True)
    tax_percentage = models.DecimalField(decimal_places=2, max_digits=4, verbose_name='Tax Percentage (%)')
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'tax'

    def __str__(self):
        return self.tax_type