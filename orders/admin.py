from django.contrib import admin

from .models import Payment,Order,OrderedPackage

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderedPackage)
