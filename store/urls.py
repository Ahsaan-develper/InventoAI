from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_home, name='user_home'),
    path('api/search/', views.product_search_api, name='product_search_api'),
    path('receipt/', views.receipt_page, name='receipt'),
]
