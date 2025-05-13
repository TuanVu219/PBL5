from django.contrib import admin
from .models import User,Role,Customer,Restaurant,TypeFood,MenuFood,ReviewMenu,Shipper,Cart,History,CartItem,FavoriteMenu,Voucher,OptionMenu,Option


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'role','email','first_name','last_name')
    
admin.site.register(Role)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user_first_name', 'user', 'age', 'phone', 'address')
    
    def user_first_name(self, obj):
     return obj.user.first_name if obj.user.first_name else obj.user.username

    user_first_name.short_description = 'First Name'  # Tên hiển thị trong cột

@admin.register(Restaurant)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('restaurant_name', 'user', 'phone_restaurant', 'address_restaurant')


@admin.register(TypeFood)
class TypeFoodAdmin(admin.ModelAdmin):
    list_display = ('type_name',)
    


@admin.register(MenuFood)
class MenuFoodAdmin(admin.ModelAdmin):
    list_display = ('restaurant','price','food_type','food_name')
    

@admin.register(ReviewMenu)
class ReviewMenuAdmin(admin.ModelAdmin):
    list_display = ('user','menu','rating','comments')
    
    
@admin.register(Shipper)
class ShipperAdmin(admin.ModelAdmin):
    list_display = ('user','age','cccd','license_plate','address','phone','vehicle')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('restaurant','customer','created_at','updated_at')
    
@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart','food','quantity')
    
@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('customer','menu','count','delivery_date')
@admin.register(FavoriteMenu)
class FavouriteMenuAdmin(admin.ModelAdmin):
    list_display = ('id',) 
@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('restaurant','value','minimum_order_value','expiration_date')

@admin.register(OptionMenu)
class OptionMenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'menu', 'option_name')
    