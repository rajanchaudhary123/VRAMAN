from django.db import models
from accounts.models import User
from vendor.models import Vendor

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
        