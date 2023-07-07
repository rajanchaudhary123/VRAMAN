from django.urls import path
from . import views
urlpatterns = [
   
   path('place_order/', views.place_order, name='place_order'),
   path('payments/', views.payments, name='payments'),
   path('order_complete/', views.order_complete, name='order_complete'),
   path('initiate_payment/', views.initiate_payment, name='initiate_payment'),
   path('return_url/', views.return_url_view, name='return_url'),
  


    ]