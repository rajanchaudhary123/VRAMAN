from django.urls import path
from . import views

urlpatterns = [
    path('', views.marketplace, name='marketplace'),


    #for collaborative recommendation
    path('', views.recommend_packages, name='recommend_packages'),
    #for interest=category
    path('', views.render_matching_packages, name='render_matching_packages'),


    path('<slug:vendor_slug>/',views.vendor_detail, name='vendor_detail'),
    #path('marketplace/review_rating/',views.review_rating, name='review_rating'),
    path('submit_review/<int:vendor_id>/',views.submit_review,name='submit_review'),

    path('submit_review_package/<int:package_id>/',views.submit_review_package,name='submit_review_package'),

    #package detail
    path('package_detail/<int:package_id>/',views.package_detail,name='package_detail'),

    # ADD TO CART
    path('add_to_cart/<int:package_id>/', views.add_to_cart, name='add_to_cart'),
    # DECREASE CART
    path('decrease_cart/<int:package_id>/', views.decrease_cart, name='decrease_cart'),
    # DELETE CART ITEM
    path('delete_cart/<int:cart_id>/', views.delete_cart, name='delete_cart'),
    
    
]