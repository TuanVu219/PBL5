from django.urls import path,include
from django.contrib import admin
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
router = routers.DefaultRouter()

urlpatterns = router.urls

urlpatterns += [
    path('admin/', admin.site.urls),
    path('user/',include('GrabFood.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)