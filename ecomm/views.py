from django.shortcuts import render

# Create your views here.
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User,inventory,Order,OrderItem
from .serializers import UserSignupSerializer, LoginSerializer, AdminLoginSerializer, UserSerializer,ProductCreateSerializer,ProductDetailSerializer,ProductListSerializer,ProductRestockSerializer,ProductUpdateSerializer,OrderItemSerializer,OrderSerializer,RevenueSerializer
import logging
from .permissions import IsShopkeeper
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_signup(request):
    """User registration endpoint"""
    try:
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            tokens = get_tokens_for_user(user)
            logger.info(f"New user registered: {user.username}")
            
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in user signup: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def user_login(request):
    """User login endpoint"""
    try:
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            logger.info(f"User logged in: {user.username}")
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in user login: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def admin_login(request):
    """Admin/Shopkeeper login endpoint"""
    try:
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            tokens = get_tokens_for_user(user)
            logger.info(f"Admin logged in: {user.username}")
            
            return Response({
                'message': 'Admin login successful',
                'user': UserSerializer(user).data,
                'tokens': tokens
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in admin login: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout(request):
    """Logout endpoint - blacklist the refresh token"""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info(f"User logged out: {request.user.username}")
            return Response({
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Refresh token required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return Response({
            'error': 'Invalid token'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_profile(request):
    """Get current user profile"""
    try:
        return Response({
            'user': UserSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def apiOverview(request):
    api_urls={
        'List':'task-list',
        'Detail view': '/task-detail/<str:pk>/',
        'create' : '/task-create/',
        'Update':'/task-update/<str:pk>',
        'Delete':'/task-delete/<str:pk>',
    }
    return Response(api_urls)


@api_view(['GET'])
@permission_classes([IsShopkeeper])
def inventory_list(request):
    tasks = inventory.objects.all()
    serializer=ProductListSerializer(tasks,many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsShopkeeper])
def inventory_detail(request,pk):
    try:
        tasks = inventory.objects.get(id=pk)
        serializer=ProductDetailSerializer(tasks,many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error retrieving inventory: {str(e)}")
        return Response({
            'error': 'Failed to retrieve inventory'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsShopkeeper])
def inventory_create(request):
    serializer=ProductCreateSerializer(data=request.data)
    try:
        if serializer.is_valid():
            product=serializer.save()
            response_serializer = ProductListSerializer(product)
            logger.info(f"Shopkeeper {request.user.username} created product: {product.name}")
            return Response({
                    'message': 'Product created successfully',
                    'product': response_serializer.data
                }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return Response({
            'error': 'Failed to create product'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)    


@api_view(['POST'])
@permission_classes([IsShopkeeper])
def inventory_update(request,pk):
     try:
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({
                'error': 'product_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = inventory.objects.get(id=product_id)
        except inventory.DoesNotExist:
            return Response({
                'error': 'Product not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            updated_product = serializer.save()
            
            response_serializer = ProductListSerializer(updated_product)
            logger.info(f"Shopkeeper {request.user.username} updated product: {updated_product.name}")
            
            return Response({
                'message': 'Product updated successfully',
                'product': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
     except Exception as e:
            logger.error(f"Error updating product: {str(e)}")
            return Response({
                'error': 'Failed to update product'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@permission_classes([permissions.IsAuthenticated, IsShopkeeper])
def restock_item(request):
    """
    POST /inventory/restock/
    Restock existing product
    Expects: product_id, quantity
    """
    try:
        serializer = ProductRestockSerializer(data=request.data)
        if serializer.is_valid():
            product_id = serializer.validated_data['product_id']
            quantity_to_add = serializer.validated_data['quantity']
            
            product = inventory.objects.get(id=product_id)
            old_quantity = product.quantity
            product.quantity += quantity_to_add
            product.last_restocked = timezone.now()
            product.save()
            
            logger.info(f"Shopkeeper {request.user.username} restocked {product.name}: {old_quantity} -> {product.quantity}")
            
            response_serializer = ProductListSerializer(product)
            return Response({
                'message': f'Product restocked successfully. Added {quantity_to_add} units.',
                'previous_quantity': old_quantity,
                'new_quantity': product.quantity,
                'product': response_serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except inventory.DoesNotExist:
        return Response({
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error restocking product: {str(e)}")
        return Response({
            'error': 'Failed to restock product'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsShopkeeper])
def view_orders(request):
    try:
        orders = Order.objects.select_related('user').prefetch_related('items__product').all()
        
        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        user_id_filter = request.query_params.get('user_id')
        if user_id_filter:
            orders = orders.filter(user_id=user_id_filter)
        
        serializer = OrderSerializer(orders, many=True)
        
        logger.info(f"Shopkeeper {request.user.username} accessed orders list")
        
        return Response({
            'message': 'Orders retrieved successfully',
            'count': len(orders),
            'orders': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        return Response({
            'error': 'Failed to retrieve orders'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsShopkeeper])
def revenue_stats(request):
    """
    GET /inventory/revenue/
    Display total revenue and statistics
    """
    try:
        # Calculate various revenue metrics
        all_orders = Order.objects.exclude(status='cancelled')
        
        # Total revenue (excluding cancelled orders)
        total_revenue = all_orders.aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        # Order counts
        total_orders = all_orders.count()
        pending_orders = all_orders.filter(status='pending').count()
        completed_orders = all_orders.filter(status='delivered').count()
        
        # Average order value
        avg_order_value = all_orders.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
        
        # Revenue this month
        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        revenue_this_month = all_orders.filter(
            created_at__gte=current_month_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Revenue this year
        current_year_start = timezone.now().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        revenue_this_year = all_orders.filter(
            created_at__gte=current_year_start
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        revenue_data = {
            'total_revenue': total_revenue,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'average_order_value': round(avg_order_value, 2) if avg_order_value else 0,
            'revenue_this_month': revenue_this_month,
            'revenue_this_year': revenue_this_year
        }
        
        serializer = RevenueSerializer(revenue_data)
        
        logger.info(f"Shopkeeper {request.user.username} accessed revenue stats")
        
        return Response({
            'message': 'Revenue statistics retrieved successfully',
            'revenue_stats': serializer.data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error calculating revenue: {str(e)}")
        return Response({
            'error': 'Failed to calculate revenue statistics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
