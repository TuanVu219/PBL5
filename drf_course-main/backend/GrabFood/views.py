from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login, logout
from .serializers import RegisterSerializer,UserSerializer,SearchSerializer,CustomerSerializer,RegisterRestaurant,Serializer_FoodType,Serializer_Menu,Serializer_ReviewMenu,Serializer_Shipper,Serializer_Cart,Serializer_CartItem,Serializer_FavouriteMenu,Serializer_Voucher,RegisterShipperSerializer, RegisterRestaurantSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics
from .models import User, Customer,Restaurant,TypeFood,MenuFood,ReviewMenu,Shipper,Cart,CartItem,FavoriteMenu,Voucher
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from json import JSONDecodeError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import traceback
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .authentication import create_access_token,create_refresh_token,decode_access_token,decode_refresh_token
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
import base64
from django.core.files.base import ContentFile
from io import BytesIO
from PIL import Image
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from .authentication import JWTAuthentication
import hmac
import hashlib
import json
from time import time
from datetime import datetime
import random
import requests
from decouple import config
import urllib.parse
from django.shortcuts import redirect
import logging
from .models import Order  # Giả sử bạn có mô hình Order
from django.http import FileResponse
import os
import uuid  # Thêm dòng này
@csrf_exempt
def zalopay_callback(request):
    if request.method == "POST":
        config = settings.ZALOPAY_CONFIG
        result = {}
        try:
            post_data = request.body.decode('utf-8')
            post_data_json = json.loads(post_data)
            data_str = post_data_json["data"]
            req_mac = post_data_json["mac"]

            # Tính toán HMAC để kiểm tra tính hợp lệ
            mac = hmac.new(
                config["key2"].encode(), data_str.encode(), hashlib.sha256
            ).hexdigest()

            if req_mac != mac:
                result["returncode"] = -1
                result["returnmessage"] = "mac not equal"
            else:
                # Thanh toán thành công, cập nhật trạng thái đơn hàng
                data_json = json.loads(data_str)
                # Ví dụ: Cập nhật trạng thái trong database
                # Order.objects.filter(app_trans_id=data_json["apptransid"]).update(status="success")
                result["returncode"] = 1
                result["returnmessage"] = "success"
        except Exception as e:
            result["returncode"] = 0  # Yêu cầu ZaloPay thử lại (tối đa 3 lần)
            result["returnmessage"] = str(e)

        return JsonResponse(result)
    return JsonResponse({"error": "Method not allowed"}, status=405)
@csrf_exempt
def create_zalopay_order(request):
    if request.method == "POST":
        config = settings.ZALOPAY_CONFIG
        order = {
            "appid": config["app_id"],
            "apptransid": "{:%y%m%d}_{}".format(datetime.today(), uuid.uuid4()),
            "appuser": data.get("appuser", "demo_user"),
            "apptime": int(round(time() * 1000)),
            "embeddata": json.dumps(data.get("embeddata", {"merchantinfo": "embeddata123"})),
            "item": json.dumps(data.get("item", [
                {"itemid": "knb", "itemname": "kim nguyen bao", "itemprice": 198400, "itemquantity": 1}
            ])),
            "amount": data.get("amount", 50000),
            "description": data.get("description", "ZaloPay Integration Demo"),
            "bankcode": data.get("bankcode", "zalopayapp"),
        }

        # Tạo chuỗi HMAC
        data = "{}|{}|{}|{}|{}|{}|{}".format(
            order["appid"], order["apptransid"], order["appuser"], order["amount"],
            order["apptime"], order["embeddata"], order["item"]
        )
        order["mac"] = hmac.new(
            config["key1"].encode(), data.encode(), hashlib.sha256
        ).hexdigest()

        # Gửi yêu cầu tới ZaloPay
        try:
            response = urllib.request.urlopen(
                url=config["endpoint"],
                data=urllib.parse.urlencode(order).encode()
            )
            result = json.loads(response.read())
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Method not allowed"}, status=405)
class ZaloPayCreateOrderView(APIView):
    def post(self, request):
        # Cấu hình ZaloPay
        zalo_config = {
            "app_id": config("ZALOPAY_APP_ID", default="4428845388423879238"),
            "key1": config("ZALOPAY_KEY1", default="XJemOIVQVt7MR9I8ZguQ"),
            "key2": config("ZALOPAY_KEY2", default="kLtgPl8HHhfvMuDHPwKfgfsY4Ydm9eIz"),
            "endpoint": "https://sb-openapi.zalopay.vn/v2/create"
        }

        trans_id = 123456  # Thay bằng random.randrange(1000000) nếu cần
        order = {
            "app_id": zalo_config["app_id"],  # Truy cập đúng từ dictionary
            "app_trans_id": f"{int(time() * 1000)}_{trans_id}",
            "app_user": "demo",
            "app_time": int(round(time() * 1000)),
            "embed_data": json.dumps({"preferred_payment_method": ["vietqr"]}),
            "item": json.dumps([{"id": "item1", "name": "Sản phẩm 1", "price": 10000, "quantity": 1}]),
            "amount": request.data.get("amount", 10000),
            "description": f"Thanh toán đơn hàng #{trans_id}",
            "bank_code": ""
        }

        # Tính MAC
        data = "|".join([str(order[k]) for k in ["app_id", "app_trans_id", "app_user", "amount", "app_time", "embed_data", "item"]])
        order["mac"] = hmac.new(zalo_config["key1"].encode(), data.encode(), hashlib.sha256).hexdigest()

        # Gửi yêu cầu
        response = requests.post(
            zalo_config["endpoint"],
            data=order,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        result = response.json()

        if result.get("return_code") == 1:
            return Response({
                "message": "Tạo đơn hàng thành công",
                "order_url": result.get("order_url"),
                "qr_code": result.get("qr_code")
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "message": "Tạo đơn hàng thất bại",
                "error": result
            }, status=status.HTTP_400_BAD_REQUEST)
def serve_verification_file(request):
    file_path = os.path.join(os.path.dirname(__file__), 'static', 'zalo_verifierHUIZSe7rUIe3mjKSs_9zGoRJqslAfGKmC3Or.html')
    return FileResponse(open(file_path, 'rb'), content_type='text/html')
def home(request):
    return render(request,'home.html')
# class PasswordResetRequestView(APIView):
#     def post(self,request):
#         email=request.data.get("email")
#         if not email:
#             return JsonResponse({"result": "error", "message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
#         user=User.objects.filter(email=email).first()
#         if user:
#             token=default_token_generator.make_token(user)
#             uid=urlsafe_base64_encode(str(user.pk).encode('utf-8'))
            
#             reset_link=get_current_site(request).domain+reverse('password_reset_confirm',kwargs={'uidb64':uid,'token':token})
#             message = render_to_string('password_reset_email.html', {
#                 'reset_link': reset_link,
#                 'user': user,
#             })     
#                     # Gửi email cho người dùng với liên kết đặt lại mật khẩu
#             subject = 'Password Reset Request'
#             send_mail(
#                 subject,              # Tiêu đề email
#                 message,              # Nội dung email
#                 'no-reply@yourdomain.com', # Email người gửi
#                 [email],              # Người nhận email
#                 fail_silently=False,  # Nếu có lỗi sẽ báo lỗi
#             )
       
#             return JsonResponse({
#                  "message": "Password reset link generated",
#                 "reset_link": reset_link
#             },status=status.HTTP_200_OK)
#         return JsonResponse({"result": "error", "message": "Email not found"}, status=status.HTTP_404_NOT_FOUND)
# class PasswordResetConfirmView(APIView):
#     def post(self, request, uidb64, token):
#         try:
#             uid = urlsafe_base64_decode(uidb64).decode()
#             user = User.objects.get(pk=uid)

#             if default_token_generator.check_token(user, token):
#                 password = request.data.get("password")
#                 if password:
#                     user.set_password(password)
#                     user.save() 
#                     return Response({"message": "Password has been successfully reset"}, status=status.HTTP_200_OK)
#                 return JsonResponse({"result": "error", "message": "Password is required"}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 return JsonResponse({"result": "error", "message": "Invalid token or expired link"}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return JsonResponse({"result": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
class RegisterView(APIView):
 def post(self, request):
    try:
        data = JSONParser().parse(request)
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self,request):
        data = JSONParser().parse(request)
        username=data.get("username")
        password=data.get("password")
        
        if username:
                user=authenticate(request,username=username,password=password)
                if user:
                    login(request,user)
                   
                    access_token = create_access_token(user.id)
                    refresh_token = create_refresh_token(user.id)
                    response=Response()
                    response.set_cookie(key="refreshToken",value=refresh_token,httponly=True,secure=False, samesite='Lax')  # tránh bị chặn bởi trình duyệt)
                    response.data={
                        'refreshToken':refresh_token,
                        'accessToken':access_token,
                        'username':user.username,
                        'password':user.password,
                        'email':user.email,
                    }
                    return response
                return Response({
                    "message":"Login Fail"
                },status=status.HTTP_404_NOT_FOUND)
               
@method_decorator(csrf_exempt, name='dispatch')  
class UserAPIView(APIView):
    def get(self, request):
        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:
            token = auth[1].decode('utf-8')
            user_id = decode_access_token(token)

            try:
                user = User.objects.filter(pk=user_id).first() # Lấy user từ model GrabFood.User
            except User.DoesNotExist:
                raise AuthenticationFailed('User not found.')

            return Response(UserSerializer(user).data)

        raise AuthenticationFailed('unauthenticated')
    
@method_decorator(csrf_exempt, name='dispatch')
class RefreshAPIView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refreshToken')
        id = decode_refresh_token(refresh_token)
        access_token = create_access_token(id)
        return Response({
            'token': access_token
        })
class LogoutView(APIView):
   def post(self, _):
        response = Response()
        response.delete_cookie(key="refreshToken")
        response.data = {
            'message': 'success'
        }
        return response
        

class UserList(generics.ListCreateAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer
    

class SearchList(APIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        data = JSONParser().parse(request)  # Lấy dữ liệu từ request
        name = data.get("name")  # Lấy giá trị 'name' từ dữ liệu
        if name:
            user = User.objects.filter(username__icontains=name)  # Lọc người dùng theo tên
            if user.exists():  # Kiểm tra nếu có người dùng khớp
                serializer = SearchSerializer(user, many=True)
                return Response(serializer.data)  # Trả về kết quả tìm kiếm
        return Response({"message": "Not found"}, status=400)  # Trả về thông báo nếu không tìm thấy

    
class DeleteUser(APIView):
    def post(self,request):
        data = JSONParser().parse(request)
        id=data.get("id")
        if id:
            try:
                user=User.objects.get(id=id)
                user.delete()
                return Response({"message":"Delete completed"},status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)    
        return Response({"message": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)    

class UpdateUser(APIView):
    def post(self,request,pk):
        if pk:
            try:
                data = JSONParser().parse(request)
                username=data.get("username")
              
                user=User.objects.get(id=pk)
                if username:
                    user.username=username
                    user.save()
                serializer=SearchSerializer(user)
                return Response(serializer.data)
            except User.DoesNotExist:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"message": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)
    
class UserDetail(generics.RetrieveUpdateDestroyAPIView): #METHOD Update:PATCH  Delete:DELETE 
    permission_classes = (IsAuthenticated,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field="pk"

class UpdateProfile(APIView):
    permission_class=(IsAuthenticated,)
    def post(self,request):
         data = JSONParser().parse(request)
         pk=data.get("pk")
         if pk:
            try:
                customer=Customer.objects.get(id=pk)
                user=User.objects.get(id=customer.user.id)

                if customer:
                    customer.user.first_name=data.get("first_name")
                    customer.user.last_name=data.get("last_name")
                    customer.user.email=data.get("email")
                    customer.age=data.get("age")
                    customer.phone=data.get("phone")
                    customer.address=data.get("address")
                    user.save()
                    customer.save()
                serializer=CustomerSerializer(customer)
                return Response(serializer.data)
            
            except Customer.DoesNotExist:
                return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
         return Response({"message": "ID is required"}, status=status.HTTP_400_BAD_REQUEST)


class Profile(APIView):
    def get(self,request,pk):
        if request.user.is_authenticated:
            customer=Customer.objects.filter(id=pk).first()
            if customer:
                serializer=CustomerSerializer(customer)
                return Response(serializer.data)
            else:
                return Response({"error": "Customer not found",
                                 "request": request.user.id if request.user.is_authenticated else "Anonymous"
                                 }, status=404)
        
        else:
            return Response({"error": "Unauthorized"}, status=401)
  

class Register_Restaurant(APIView):
  def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = RegisterRestaurantSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
                return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
        

class Restaurant_Retrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset=Restaurant.objects.all()
    serializer_class=RegisterRestaurant
    lookup_field="pk"
            
        

class RestaurantList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        # Lấy tất cả các nhà hàng từ cơ sở dữ liệu
        if request.user.is_authenticated:
            restaurants = Restaurant.objects.all()
            serializer = RegisterRestaurant(restaurants, many=True, context={'request': request})
            
            return Response(serializer.data)
        else:
            return Response({"error": "Unauthorized"}, status=401)
  
class AddFoodType(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
            if isinstance(data,list):
                serializer=Serializer_FoodType(data=data,many=True)
            else:
                serializer=Serializer_FoodType(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # Trả về phản hồi thành công
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

class FoodTypeList(generics.ListCreateAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = Serializer_FoodType

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return TypeFood.objects.all()
        else:
            return TypeFood.objects.none()  # hoặc raise PermissionDenied nếu cần

    def list(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
        return super().list(request, *args, **kwargs)
class FoodType_Retrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset=TypeFood.objects.all()
    serializer_class=Serializer_FoodType
    lookup_field="pk"
    def get(self, request, *args, **kwargs):
        # Đây là phương thức GET để lấy dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().get(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        
        # Đây là phương thức PATCH để cập nhật dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Đây là phương thức DELETE để xóa dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().delete(request, *args, **kwargs)
class AddMenu(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
            if isinstance(data,list):
                serializer=Serializer_Menu(data=data,many=True)
            else:
                serializer=Serializer_Menu(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)  # Trả về phản hồi thành công
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)


class MenuList(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request):
        if self.request.user.is_authenticated:
            try:
                # Lấy restaurant_id từ dữ liệu gửi lên trong POST
                restaurant_id = request.data.get('restaurant')

                if not restaurant_id:
                    return Response({"error": "restaurant_id is required"}, status=status.HTTP_400_BAD_REQUEST)
                
                # Lấy nhà hàng từ ID
                restaurant = Restaurant.objects.get(id=restaurant_id)
                menu = MenuFood.objects.filter(restaurant=restaurant)

                # Serialize dữ liệu
                serializer = Serializer_Menu(menu, many=True, context={'request': request})

                return Response(serializer.data, status=status.HTTP_200_OK)  # Trả về phản hồi thành công

            except Restaurant.DoesNotExist:
                return Response({"error": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

class Menu_Retrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuFood.objects.all()  # Khai báo queryset ở đây
    serializer_class = Serializer_Menu
    lookup_field = 'pk'
    def get(self, request, *args, **kwargs):
        # Đây là phương thức GET để lấy dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().get(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        
        # Đây là phương thức PATCH để cập nhật dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Đây là phương thức DELETE để xóa dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().delete(request, *args, **kwargs)

class AddReviewMenu(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
            serializers=Serializer_ReviewMenu(data=data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

class ReviewMenu_Retrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset = ReviewMenu.objects.all()  # Khai báo queryset ở đây
    serializer_class = Serializer_ReviewMenu
    lookup_field = 'pk'
    def get(self, request, *args, **kwargs):
        # Đây là phương thức GET để lấy dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().get(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        
        # Đây là phương thức PATCH để cập nhật dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Đây là phương thức DELETE để xóa dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().delete(request, *args, **kwargs)

class ListReviewMenu(APIView):  
        def get(self,request,pk):
            try:
                review=ReviewMenu.objects.filter(menu=pk)
                serializer=Serializer_ReviewMenu(review,many=True)
                if serializer:
                    return Response(serializer.data, status=status.HTTP_200_OK)  # Trả về phản hồi thành công
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            except:
                 return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

class RegisterShipper(APIView):
    def post(self, request):
        try:
            data = JSONParser().parse(request)
            serializer = RegisterShipperSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
                return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
        
class Shipper_Retrieve(generics.RetrieveUpdateDestroyAPIView):
    queryset = Shipper.objects.all()  # Khai báo queryset ở đây
    serializer_class = Serializer_Shipper
    lookup_field = 'pk'
    def get(self, request, *args, **kwargs):
        # Đây là phương thức GET để lấy dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().get(request, *args, **kwargs)
    
    def patch(self, request, *args, **kwargs):
        
        # Đây là phương thức PATCH để cập nhật dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # Đây là phương thức DELETE để xóa dữ liệu
        if not request.user.is_authenticated:
            return Response({"error": "Unauthorized"}, status=401)
        return super().delete(request, *args, **kwargs)
            
class AddCart(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
            serializers=Serializer_Cart(data=data)
            if serializers.is_valid():
                serializers.save()
                return Response(serializers.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)

class SearchCart(APIView):
    def get(self,request,id_customer,id_restaurant):
        cart=Cart.objects.filter(
            restaurant=id_restaurant,
            customer=id_customer
        ).first()
        if cart:
          serializer=Serializer_Cart(cart)
          if serializer:
            return Response(serializer.data, status=status.HTTP_201_CREATED)
          else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"result": "error","message": "Cart not found"}, status= 400)


class DeleteCart(APIView):
    def delete(self,request,id_customer,id_restaurant):
        try:
            cart=Cart.objects.filter(
                customer=id_customer,
                restaurant=id_restaurant
            ).first()
            if cart:
                cart.delete()
                return Response({"result": "success", "message": "Cart deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"result": "error", "message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
class AddCartItem(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
           
            customer_id = data.get("customer")
            restaurant_id = data.get("restaurant")
            
            if not customer_id or not restaurant_id:
                return Response({"result": "error", "message": "Customer and Restaurant are required"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                customer = Customer.objects.get(id=customer_id)
                restaurant = Restaurant.objects.get(id=restaurant_id)
            except Customer.DoesNotExist:
                return Response({"result": "error", "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
            except Restaurant.DoesNotExist:
                return Response({"result": "error", "message": "Restaurant not found"}, status=status.HTTP_404_NOT_FOUND)
                
            
            cart=Cart.objects.filter(customer=customer,restaurant=restaurant).first()
            if not cart:
                cart=Cart.objects.create(customer=customer,restaurant=restaurant)
            data["cart"]=cart.id
            data.pop("customer",None)
            data.pop("restaurant",None)
            serializer=Serializer_CartItem(data=data)
            
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except JSONDecodeError:
            return Response({"result": "error", "message": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"result": "er6yyror", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class CartItem_List(APIView):
    def get(self,request,id_cart):
        cart=Cart.objects.get(id=id_cart)
        if cart:
            cart_item=CartItem.objects.filter(cart=cart)
            serializer=Serializer_CartItem(cart_item,many=True)
            if serializer:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return JsonResponse({"result": "error","message": "CartItem not found"}, status= 400)     
class DeleteCartItem(APIView):
    def delete(self,request,id_cartitem,id_food):
        try:
            cartitem=CartItem.objects.filter(
                cart=id_cartitem,
                food=id_food
            ).first()
            if cartitem:
                cartitem.delete()
                return Response({"result": "success", "message": "Cart deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"result": "error", "message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"result": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
class AddFavouriteMenu(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
            serializer=Serializer_FavouriteMenu(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
class ListFavouriteMenu(APIView):
    def get(self, request):
        try:
            user = request.user
            customer=Customer.objects.get(user=user)
            favourite_menus = FavoriteMenu.objects.filter(customer=customer)
            
            serializer = Serializer_FavouriteMenu(favourite_menus, many=True)
            
            if serializer:
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return JsonResponse({"result": "error", "message": str(e)}, status=400)    
       
class DeleteFavouriteMenu(APIView):
    def delete(self,request):
        try:
            data=JSONParser().parse(request)
            user = request.user
            customer=Customer.objects.get(user=user)
            favourite=FavoriteMenu.objects.filter(
                customer=customer,
                menu=data['menu']
            )
            if favourite:
                favourite.delete()
                return Response({"result": "success", "message": "FavouriteMenu deleted"}, status=status.HTTP_200_OK)
            else:
                return Response({"result": "error", "message": "FavouriteMenu not found"}, status=status.HTTP_404_NOT_FOUND)
           
        except Exception as e:
            return JsonResponse({"result": "error", "message": str(e)}, status=400)   

class AddVoucher(APIView):
    def post(self,request):
        try:
            data=JSONParser().parse(request)
            serializer=Serializer_Voucher(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"result": "error","message": "Json decoding error"}, status= 400)
        
            
            
       
        