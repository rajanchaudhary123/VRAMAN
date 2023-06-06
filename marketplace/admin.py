from django.contrib import admin
from .models import ReviewRating,ReviewRatingPackage
from .models import Cart,Tax




class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'packageitem', 'quantity', 'updated_at')
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active')

# Register your models here.
admin.site.register(ReviewRating)

admin.site.register(Cart, CartAdmin)

admin.site.register(ReviewRatingPackage)

admin.site.register(Tax, TaxAdmin)

