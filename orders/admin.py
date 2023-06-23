from django.contrib import admin

from .models import Payment,Order,OrderedPackage

class OrderPackageInline(admin.TabularInline):
    model = OrderedPackage
    readonly_fields=('order','payment','user','packageitem','quantity','price','amount')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display =['order_number','name','phone','email','total','payment_method','status','order_placed_to','is_ordered']
    inlines = [OrderPackageInline]
class OrderedPackageAdmin(admin.ModelAdmin):
    list_display =['id','packageitem']
    


admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderedPackage,OrderedPackageAdmin)
