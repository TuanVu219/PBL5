from rest_framework import serializers
from .models import User, Role,Customer,Restaurant,TypeFood,MenuFood,ReviewMenu,Shipper,Cart,CartItem,FavoriteMenu,Voucher
from django.contrib.auth.password_validation import validate_password
import base64
from io import BytesIO
from PIL import Image

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'password_confirmation', 'role','email','first_name','last_name')

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords must match.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirmation')
        
        role = validated_data.pop('role', None) or Role.objects.filter(role_name="Customer").first()
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            role=role,

        )

    
        customer = Customer.objects.create(user=user)
        if role:
            user.role = role
        
        user.save()
        customer.save()
        return user
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("username","password","email","first_name","last_name")
        
class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=("id","username","password")
        

class CustomerSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', allow_blank=True, required=False)
    last_name = serializers.CharField(source='user.last_name', allow_blank=True, required=False)
    email = serializers.EmailField(source='user.email', allow_blank=True, required=False)
    class Meta:
        model=Customer
        fields=("age","phone","address","email","first_name","last_name")
        
class RegisterRestaurant(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = ("id", "restaurant_name", "phone_restaurant", "address_restaurant", "image","user")
    def get_image(self, obj):
        return obj.image.url if obj.image else None
class Serializer_FoodType(serializers.ModelSerializer):
    class Meta:
        model=TypeFood
        fields=("type_name",)

class Serializer_Menu(serializers.ModelSerializer):
    food_type = serializers.StringRelatedField()
    restaurant = serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())
    image = serializers.ImageField(required=False) 
    class Meta:
        model=MenuFood
        fields=("restaurant","price","food_type","food_name",'image')
    def get_image(self, obj):
        return obj.image.url if obj.image else None

class Serializer_ReviewMenu(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    menu = serializers.PrimaryKeyRelatedField(queryset=MenuFood.objects.all())
    class Meta:
        model=ReviewMenu
        fields=("user","menu","rating","comments")


class Serializer_Shipper(serializers.ModelSerializer):
    class Meta:
        model=Shipper
        fields=('user','age','cccd','license_plate','address','phone','vehicle')
class RegisterShipperSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)

    age = serializers.IntegerField(write_only=True)
    cccd = serializers.CharField(write_only=True)
    license_plate = serializers.CharField(write_only=True)
    address = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    vehicle = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            'username', 'password', 'password_confirmation', 'role', 'email',
            'first_name', 'last_name', 'age', 'cccd', 'license_plate', 'address', 'phone', 'vehicle'
        )

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')

        role = validated_data.pop('role', None) or Role.objects.filter(role_name="Shipper").first()
        age = validated_data.pop('age')
        cccd = validated_data.pop('cccd')
        license_plate = validated_data.pop('license_plate')
        address = validated_data.pop('address')
        phone = validated_data.pop('phone')
        vehicle = validated_data.pop('vehicle')

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            role=role
        )
        
        Shipper.objects.create(
            user=user,
            age=age,
            cccd=cccd,
            license_plate=license_plate,
            address=address,
            phone=phone,
            vehicle=vehicle
        )

        return user
class RegisterRestaurantSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirmation = serializers.CharField(write_only=True, required=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)

 
    restaurant_name= serializers.CharField(write_only=True)
    address_restaurant = serializers.CharField(write_only=True)
    phone_restaurant = serializers.CharField(write_only=True)
    image = serializers.ImageField(required=False)  # Image có thể bỏ qua khi tạo mới

    class Meta:
        model = User
        fields = (
            'username', 'password', 'password_confirmation', 'role', 'email',
            'first_name', 'last_name','restaurant_name', 'address_restaurant', 'phone_restaurant','image'
        )

    def validate(self, data):
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError("Passwords must match.")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirmation')

        role = validated_data.pop('role', None) or Role.objects.filter(role_name="Host").first()
        restaurant_name=validated_data.pop('restaurant_name')
        address_restaurant = validated_data.pop('address_restaurant')
        phone_restaurant = validated_data.pop('phone_restaurant')
        image = validated_data.pop('image', None)  # Nếu có ảnh gửi lên sẽ sử dụng
        
        if not image:
            image = 'images/default-ui-image-placeholder-wireframes-600nw-1037719192.webp'

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            role=role
        )
        
        Restaurant.objects.create(
            user=user,
            restaurant_name=restaurant_name,
            address_restaurant=address_restaurant,
            phone_restaurant=phone_restaurant,  
            image=image,


        )

        return user

class Serializer_Cart(serializers.ModelSerializer):
    class Meta:
        model=Cart
        fields=('restaurant','customer','created_at','updated_at')
class Serializer_CartItem(serializers.ModelSerializer):
    class Meta:
        model=CartItem
        fields=('cart','food','quantity')
class Serializer_FavouriteMenu(serializers.ModelSerializer):
    class Meta:
        model=FavoriteMenu
        fields=('customer','menu')
class Serializer_Voucher(serializers.ModelSerializer):
    class Meta:
        model=Voucher
        fields=('restaurant','value','minimum_order_value','expiration_date')