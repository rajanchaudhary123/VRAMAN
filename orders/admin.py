from django.contrib import admin

from .models import Payment,Order,OrderedPackage

class OrderPackageInline(admin.TabularInline):
    model = OrderedPackage
    readonly_fields=('order','payment','user','packageitem','quantity','price','amount')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display =['order_number','name','phone','total','payment_method','status','is_ordered']
    inlines = [OrderPackageInline]

admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderedPackage)
