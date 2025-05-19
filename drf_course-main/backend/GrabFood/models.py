from django.db import models
from django.contrib.auth.models import AbstractUser,Group, Permission
from utils.model_abstracts import Model
from django.core.validators import RegexValidator
from django.core.validators import MaxValueValidator, MinValueValidator
from cloudinary.models import CloudinaryField
from django_extensions.db.models import (
	TimeStampedModel, 
	ActivatorModel,
	TitleDescriptionModel
)
from uuid import uuid4

# Create your models here.
class Role(Model):
    role_name=models.CharField(max_length=120)

    def __str__(self):
        return self.role_name
class User(AbstractUser,Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions_set', blank=True)
    first_name=models.CharField(max_length=30,blank=False,null=False)
    last_name=models.CharField(max_length=30,blank=False,null=False)
    email_validator=RegexValidator(
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        message='Enter a valid email address.'
    )
    email = models.EmailField(
        unique=True, 
        blank=False, 
        null=False, 
        validators=[email_validator]
    ) 
    
    
    def __str__(self):
        return self.username

class Customer(Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="customer_user")
    age=models.IntegerField(null=True, blank=True)
    phone=models.CharField(max_length=10,unique=True,
                           null=True, blank=True,
                          validators=[RegexValidator(r'^\d{10}$', 'Enter a valid phone number with exactly 10 digits')])
    address=models.CharField(max_length=100)
    

    def __str__(self):
        return self.user.first_name if self.user.first_name else self.user.username
    
class Restaurant(Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="restaurant_user")
    restaurant_name=models.CharField(max_length=100)
    phone_restaurant=models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid phone number with exactly 10 digits')]
    )
    address_restaurant=models.CharField(max_length=100)
    image = CloudinaryField('image', default='images/default-ui-image-placeholder-wireframes-600nw-1037719192.webp')
    def __str__(self):
        return self.restaurant_name
class TypeFood(Model):
    type_name = models.CharField(max_length=100)
    image = CloudinaryField('image', default='images/default-ui-image-placeholder-wireframes-600nw-1037719192.webp')


    def __str__(self):
        return self.type_name

class MenuFood(Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_menu')
    description= models.TextField(null=True, blank=True)
    time=models.DurationField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    food_type = models.ForeignKey(TypeFood, on_delete=models.CASCADE, related_name="foodtype")
    food_name = models.CharField(max_length=100, null=False)
    image = CloudinaryField('image', default='images/default-ui-image-placeholder-wireframes-600nw-1037719192.webp')

    def __str__(self):
        return f"{self.food_name} at {self.restaurant.restaurant_name}"
class Order(models.Model):
    order_id = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    order_desc = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    def __str__(self):
        return self.order_id
class OptionMenu(Model):
    menu=models.ForeignKey(MenuFood, on_delete=models.CASCADE, related_name='option_menu')
    option_name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10, decimal_places=2, blank=True,default=0)
    def __str__(self):
        return self.option_name
class Option(Model):
    menu=models.ForeignKey(MenuFood, on_delete=models.CASCADE, related_name='menu_option')
    option_name=models.CharField(max_length=100)
    def __str__(self):
        return self.option_name
class ReviewMenu(Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_review")
    menu=models.ForeignKey(MenuFood,on_delete=models.CASCADE,related_name="menu_review")
    rating=models.IntegerField(
        null=False,
        blank=False,
        validators=[MinValueValidator(1),MaxValueValidator(5)]
    )
    comments=models.CharField(null=True,blank=True,max_length=100)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_created=True)
    def __str__(self):
        return f"Review by {self.user} for {self.menu}"

class Shipper(Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name="shipper_user")
    age=models.IntegerField(blank=False,null=False)
    cccd=models.CharField(
        max_length=12,
        validators=[RegexValidator(r'^\d{12}$', 'Enter a valid phone number with exactly 12 digits')]
    )
    license_plate=models.CharField(
        max_length=15,
        validators=[RegexValidator(r'^[A-Z0-9 -]{5,15}$', 'Enter a valid license plate')]
    )
    address=models.CharField(max_length=100)
    phone=models.CharField(max_length=100)
    vehicle=models.CharField(max_length=100)  

class Cart(Model):
    restaurant=models.OneToOneField(Restaurant,on_delete=models.CASCADE,related_name='restaurant_carts')
    customer=models.ForeignKey(Customer,on_delete=models.CASCADE,related_name='carts')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 
        
    def __str__(self):
        return f"Cart for {self.customer.user.username}"
    
class CartItem(Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    food=models.ForeignKey(MenuFood,on_delete=models.CASCADE,related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    def __str__(self):
        return f"{self.quantity} of {self.food.food_name} in cart for {self.cart.customer.user.username}"

class History(Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='histories')
    menu = models.ForeignKey(MenuFood, on_delete=models.CASCADE, related_name='histories')
    count=models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Số lượng món ăn đã đặt trong lịch sử."
    )
    delivery_date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"History: {self.customer.user.username} - {self.menu.food_name} x {self.count}"
class FavoriteMenu(Model):
    customer=models.ManyToManyField(Customer, related_name='customuser_favouritemenu')
    menu=models.ManyToManyField(MenuFood,related_name='menu_favouritemenu')
    
class Voucher(Model):
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name="vouchers")
    value=models.IntegerField( null=False, blank=False)
    minimum_order_value = models.IntegerField(null=False, blank=False)
    expiration_date = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return f"Voucher {self.id} - Value: {self.value}"