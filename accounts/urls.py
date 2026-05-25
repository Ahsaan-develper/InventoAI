from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("adminLogin/", views.admin_login_view, name="admin_login"),
    path("adminSignup/", views.admin_signup_view, name="admin_signup"),
    
    # Admin routes
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/addItems/', views.add_item_view, name='add_items'),
    path('admin/showItems/', views.show_items_view, name='show_items'),
    path('admin/updateItem/<int:pk>/', views.update_item_view, name='update_item'),
    path('admin/deleteItem/<int:pk>/', views.delete_item_view, name='delete_item'),
    
    # User routes — NEW
    path('user/', views.user_home, name='user_home'),

]