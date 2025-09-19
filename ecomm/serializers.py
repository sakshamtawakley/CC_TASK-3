from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User,inventory,Category,Order,OrderItem

class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            **validated_data,
            role='user'  # Default role for new signups
        )
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must provide username and password')
        
        return attrs

class AdminLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = attrs['user']
        
        if user.role != 'shopkeeper':
            raise serializers.ValidationError('Access denied. Admin privileges required.')
        
        return attrs

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'created_at')
        read_only_fields = ('id', 'role', 'created_at')

#Inventory management
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']

class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for inventory list - shows essential info"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = inventory
        fields = ['id', 'name', 'category_name', 'quantity', 'price', 'created_at', 'last_restocked']

class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product operations"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = inventory
        fields = [
            'id', 'name', 'description', 'category', 'category_id', 
            'price', 'quantity', 'created_at', 'updated_at', 'last_restocked'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new products"""
    class Meta:
        model = inventory
        fields = ['name', 'description', 'category', 'price', 'quantity']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value

class ProductUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating existing products"""
    class Meta:
        model = inventory
        fields = ['name', 'description', 'category', 'price', 'quantity']
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value

class ProductRestockSerializer(serializers.Serializer):
    """Serializer for restocking products"""
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_product_id(self, value):
        try:
            inventory.objects.get(id=value)
        except inventory.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        
        return value
    
class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'subtotal']

class OrderSerializer(serializers.ModelSerializer):
    """Serializer for viewing orders"""
    items = OrderItemSerializer(many=True, read_only=True)
    user_info = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            'id', 'user_info', 'total_amount', 'status', 
            'shipping_address', 'phone_number',
            'created_at', 'updated_at', 'items'
        ]
    
    def get_user_info(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'first_name': obj.user.first_name,
            'last_name': obj.user.last_name
        }
class RevenueSerializer(serializers.Serializer):
    """Serializer for revenue statistics"""
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    revenue_this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    revenue_this_year = serializers.DecimalField(max_digits=15, decimal_places=2)