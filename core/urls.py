"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from suoi_tien import views

urlpatterns = [
    # Django Admin gốc với giao diện Unfold
    path('admin/', admin.site.urls),
    
    # Custom FE Admin
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('posts/', views.post_list, name='post_list'),
    path('products/', views.product_list, name='product_list'),
    path('comments/', views.comment_list, name='comment_list'),
    path('comments/toggle/<int:pk>/', views.toggle_comment_status, name='toggle_comment_status'),
    path('comments/reply/<int:pk>/', views.reply_comment, name='reply_comment'),
    path('support/', views.support_list, name='support_list'),
    path('support/toggle/<int:pk>/', views.toggle_support_status, name='toggle_support_status'),
    path('orders/', views.ticket_orders, name='ticket_orders'),
    path('food-orders/', views.food_orders, name='food_orders'),
    path('settings/', views.settings_view, name='settings_view'),
]
