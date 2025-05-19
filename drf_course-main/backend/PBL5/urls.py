from django.urls import path,include
from django.contrib import admin
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from GrabFood.views import serve_verification_file
router = routers.DefaultRouter()

urlpatterns = router.urls
def health_check(request):
    return HttpResponse("Application is running", content_type="text/plain")

urlpatterns += [
    path('admin/', admin.site.urls),
    path('user/',include('GrabFood.urls')),
    path('health/', health_check, name='health_check'),
    path('zalo_verifierHUIZSe7rUIe3mjKSs_9zGoRJqslAfGKmC3Or.html', serve_verification_file),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)