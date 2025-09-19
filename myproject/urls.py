"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from ecomm import views
urlpatterns = [
    # User authentication
    path('auth/user/signup/', views.user_signup, name='user_signup'),
    path('auth/user/login/', views.user_login, name='user_login'),
    
    # Admin authentication
    path('auth/admin/login/', views.admin_login, name='admin_login'),
    
    # Common endpoints
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    path('inventory/list/', views.inventory_list, name='inventory_list'),
    path('inventory/new/', views.create_item, name='create_item'),
    path('inventory/update/', views.update_item, name='update_item'),
    path('inventory/restock/', views.restock_item, name='restock_item'),
    path('inventory/orders/', views.view_orders, name='view_orders'),
    path('inventory/revenue/', views.revenue_stats, name='revenue_stats'),
    path('admin/', admin.site.urls),
]
