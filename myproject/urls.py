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
from django.urls import path,include
from ecomm import views
urlpatterns = [
    # User authentication
    path('auth/user/signup/', views.user_signup, name='user_signup'),
    path('auth/user/login/', views.user_login, name='user_login'),
    
    # Admin authentication
    path('auth/admin/login/', views.admin_login, name='admin_login'),
    
    # Shop endpoints
    path('shop/list/', views.shop_item_list, name='shop-item-list'),
    path('shop/item/<int:item_id>/', views.shop_item_detail, name='shop-item-detail'),
    path('shop/categories/', views.shop_categories, name='shop-categories'),
    
    # Order endpoints
    path('orders/past/', views.order_list, name='order-list'),
    path('orders/new/', views.create_order, name='create-order'),
    path('orders/<int:order_id>/', views.order_detail, name='order-detail'),

    # Common endpoints
    path('auth/logout/', views.logout, name='logout'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    path('inventory/list/', views.inventory_list, name='inventory_list'),
    path('inventory/new/', views.inventory_create, name='create_item'),
    path('inventory/update/', views.inventory_update, name='update_item'),
    path('inventory/restock/', views.restock_item, name='restock_item'),
    path('inventory/orders/', views.view_orders, name='view_orders'),
    path('inventory/revenue/', views.revenue_stats, name='revenue_stats'),
    path('categories/', views.list_categories, name='list_categories'),
<<<<<<< HEAD
=======

>>>>>>> 519818360dee6caac26d031b0e1f580103c5fb5a
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]
