from django.urls import path,include
from . import views
from accounts import views as AccountViews

urlpatterns = [
    path('', AccountViews.vendorDashboard, name='vendor'),
    path('profile/', views.vprofile, name='vprofile'),
    path('menu-builder',views.menu_builder, name='menu_builder'),
    path('menu-builder-category/<int:pk>/', views.packageitems_by_category, name='packageitems_by_category'),
    
    #category CRUD
    path('menu-builder/category/add/', views.add_category, name='add_category'),
    path('menu-builder/category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('menu-builder/category/delete/<int:pk>/', views.delete_category, name='delete_category'),
    
     # FoodItem CRUD
      path('menu-builder/package/add/', views.add_package, name='add_package'),
       path('menu-builder/package/edit/<int:pk>/', views.edit_package, name='edit_package'),
       path('menu-builder/package/delete/<int:pk>/', views.delete_package, name='delete_package'),
]