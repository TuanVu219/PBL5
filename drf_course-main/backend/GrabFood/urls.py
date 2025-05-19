from django.urls import path, include
from django.contrib import admin
from rest_framework import routers
from .views import (
    RegisterView, LoginView, LogoutView, UserList, SearchList, DeleteUser,
    UpdateUser, UserDetail, UpdateProfile, Profile, Register_Restaurant, 
    Restaurant_Retrieve, RestaurantList, AddFoodType, FoodTypeList, 
    FoodType_Retrieve, AddMenu, MenuList, Menu_Retrieve, AddReviewMenu, 
    ListReviewMenu, ReviewMenu_Retrieve, RegisterShipper, Shipper_Retrieve, 
    AddCart, SearchCart,AddFavouriteMenu,ListFavouriteMenu,DeleteFavouriteMenu,AddCartItem,CartItem_List,DeleteCartItem,AddVoucher,UserAPIView,
    RefreshAPIView,ZaloPayCreateOrderView, serve_verification_file
)
from rest_framework.authtoken.views import obtain_auth_token
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
router = routers.DefaultRouter()

urlpatterns = router.urls
# Nguoi dung URL
urlpatterns += [
    path('register/', RegisterView.as_view(), name='register'),
    path('user/', UserAPIView.as_view(), name='user'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
    path('refresh-token/', RefreshAPIView.as_view(), name='refresh_token'),
]
#Zalopay
urlpatterns += [
  path('create-order/', ZaloPayCreateOrderView.as_view(), name='zalopay-create-order'),
  path('zalo_verifierHUIZSe7rUle3mjKSs_9zGoRJqslAfGKmC3Or.html', serve_verification_file),
  path('zalopay/create-order/', views.create_zalopay_order, name='create_order'),
  path('zalopay/callback/', views.zalopay_callback, name='callback'),
]
# QUan ly nguoi dung URL
urlpatterns += [
    path('list_user/', UserList.as_view(), name='userlist'),
    path('search/', SearchList.as_view(), name='searchlist'),
    path('delete/', DeleteUser.as_view(), name='deletelist'),
    path('update/<uuid:pk>/', UpdateUser.as_view(), name='userupdate'),
    path('retrieve/<uuid:pk>/', UserDetail.as_view(), name='userdetail'),
    path('update-profile/', UpdateProfile.as_view(), name='updateprofile'),
    path('profile/<uuid:pk>/', Profile.as_view(), name='profile'),
]

# Quan ly nha hang URL
urlpatterns += [
    path('register_restaurant/', Register_Restaurant.as_view(), name='registerrestaurant'),
    path('retrieve_restaurant/<uuid:pk>/', Restaurant_Retrieve.as_view(), name='restaurant_retrieve'),
    path('restaurant_list/', RestaurantList.as_view(), name='restaurant_list'),
]

# Type do an URL
urlpatterns += [
    path('add_typefood/', AddFoodType.as_view(), name='add_foodtype'),
    path('list_typefood/', FoodTypeList.as_view(), name='list_foodtype'),
    path('retrieve_typefood/<uuid:pk>/', FoodType_Retrieve.as_view(), name='retrieve_foodtype'),
]

# Menu URL
urlpatterns += [
    path('addmenu/', AddMenu.as_view(), name='add_menu'),
    path('menulist/', MenuList.as_view(), name='menu_list'),
    path('retrieve_menu/<uuid:pk>/', Menu_Retrieve.as_view(), name='retrieve_menu'),
]

# Quan ly Review URL
urlpatterns += [
    path('addreview/', AddReviewMenu.as_view(), name='add_reviewmenu'),
    path('list_reviewmenu/<uuid:pk>/', ListReviewMenu.as_view(), name='listreviewmenu'),
    path('retrieve_reviewmenu/<uuid:pk>/', ReviewMenu_Retrieve.as_view(), name='retrieve_reviewmenu'),
]

# Shipper URL
urlpatterns += [
    path('register_shipper/', RegisterShipper.as_view(), name='register_shipper'),
    path('retrieve_shipper/<uuid:pk>/', Shipper_Retrieve.as_view(), name='retrieve_shipper'),
]

# Cart URL
urlpatterns += [
    path('addcart/', AddCart.as_view(), name='add_cart'),
    path('searchcart/<uuid:id_customer>/<uuid:id_restaurant>/', SearchCart.as_view(), name='search_cart'),
]

# Password Reset URL
urlpatterns += [
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), name="password_reset_complete"),
]

# Social Authentication URL
urlpatterns += [
    path('auth/', include('social_django.urls', namespace='social')),
]

# Miscellaneous URL
urlpatterns += [
    path('', views.home, name='home'),
]

#FavouriteMenu Urls
urlpatterns += [
    path('add_favouritemenu/', AddFavouriteMenu.as_view(), name='add_favouritemenu'),
    path('list_favouritemenu/', ListFavouriteMenu.as_view(), name='list_favouritemenu'),
    path('delete_favouritemenu/', DeleteFavouriteMenu.as_view(), name='delete_favouritemenu'),

]

#CartItem Urls
urlpatterns += [
    path('add_cartitem/', AddCartItem.as_view(), name='add_cartitem'),
    path('list_cartitem/<uuid:id_cart>/', CartItem_List.as_view(), name='list_cartitem'),
    path('delete_cartitem/', DeleteCartItem.as_view(), name='delete_cartitem'),
]

#Voucher Urls
urlpatterns += [
    path('add_voucher/', AddVoucher.as_view(), name='add_voucher'),
 
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)