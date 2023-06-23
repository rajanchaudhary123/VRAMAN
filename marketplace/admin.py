from django.contrib import admin
from .models import ReviewRating,ReviewRatingPackage
from .models import Cart,Tax
from .models import CollaborativeRecommendation
from .models import ContentRecommendation
from .models import SentimentRecommendation

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'packageitem', 'quantity', 'updated_at')
class TaxAdmin(admin.ModelAdmin):
    list_display = ('tax_type', 'tax_percentage', 'is_active')
class ColabAdmin(admin.ModelAdmin):
    list_display = ('user',)
    
class ContentAdmin(admin.ModelAdmin):
    list_display = ('user',)

class SentimentAdmin(admin.ModelAdmin):
    list_display = ('user',)


# Register your models here.
admin.site.register(ReviewRating)

admin.site.register(Cart, CartAdmin)

admin.site.register(ReviewRatingPackage)

admin.site.register(Tax, TaxAdmin)

admin.site.register(CollaborativeRecommendation, ColabAdmin)
admin.site.register(ContentRecommendation, ContentAdmin)

admin.site.register(SentimentRecommendation, SentimentAdmin)