from pathlib import Path
from dotenv import load_dotenv
import os
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = int(os.environ.get("DEBUG", default=0))
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(" ")

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions', #Great packaged to access abstract models
    'django_filters', #Used with DRF
    'rest_framework', #DRF package
    'GrabFood', # New app
    'rest_framework.authtoken',
    'social_django',
    'django_celery_beat',
     'corsheaders',
     'django_celery_results',
]
# RabbitMQ broker
CELERY_BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# Redis làm backend (hoặc bạn có thể dùng database backend)
CELERY_RESULT_BACKEND = 'django-db'
# (Tùy chọn) Các cấu hình khác
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Ho_Chi_Minh'
broker_connection_retry_on_startup = True
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',  
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]
CORS_ALLOW_ALL_ORIGINS = True
CSRF_COOKIE_HTTPONLY = True
CORS_ORIGIN_ALLOW_ALL = True
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']
CORS_ALLOWED_ORIGINS = [
    'http://example.com',
    'http://172.20.10.4:8000',
]
CORS_ALLOW_METHODS = [
    'GET',
    'POST',
    'PUT',
    'DELETE',
]
CORS_ALLOW_HEADERS = [
    'content-type',
    'authorization',
]
CORS_ALLOW_CREDENTIALS = True
ROOT_URLCONF = 'PBL5.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',  
                'social_django.context_processors.backends', 
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'social_core.backends.facebook.FacebookOAuth2',
    'social_core.backends.twitter.TwitterOAuth',
    'social_core.backends.github.GithubOAuth2',

    'django.contrib.auth.backends.ModelBackend',
)


LOGIN_URL = 'login'
LOGOUT_URL = 'logout'
LOGIN_REDIRECT_URL = 'home'


SOCIAL_AUTH_FACEBOOK_KEY = '1652171999016910'  
SOCIAL_AUTH_FACEBOOK_SECRET = '86c297890ad7fe6c6d84cf55d0f3c845' 

WSGI_APPLICATION = 'PBL5.wsgi.application'

ROOT_URLCONF = 'PBL5.urls'

AUTH_USER_MODEL = 'GrabFood.User'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    # Loại bỏ JSON:API exception handler và thay bằng mặc định của DRF
    'EXCEPTION_HANDLER': 'rest_framework_json_api.exceptions.exception_handler',
    
    # Sử dụng JSONParser của DRF thay vì JSON:API
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',  # Phân tích yêu cầu JSON thuần túy
    ),
    
    # Sử dụng JSONRenderer của DRF để trả về JSON thuần túy
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  # Trả về dữ liệu dưới dạng JSON
        'rest_framework.renderers.BrowsableAPIRenderer',  # Cho phép duyệt API qua trình duyệt
    ),
    
    # Metadata mặc định của DRF
    'DEFAULT_METADATA_CLASS': 'rest_framework.metadata.SimpleMetadata',
    
    # Các filter backend mặc định của DRF
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
        'django_filters.rest_framework.DjangoFilterBackend',  # Dùng filter backend của Django Filters
    ),
    
    # Param tìm kiếm mặc định
    'SEARCH_PARAM': 'search',
    
    # Cấu hình cho các lớp renderer trong môi trường test
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',  # Sử dụng JSONRenderer cho môi trường test
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',  # Định dạng mặc định là JSON
    
    # Thêm cấu hình xác thực
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',  # Dùng TokenAuthentication cho JWT
    ),
}
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Hoặc server SMTP bạn sử dụng
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'doancongtuanvudn2004@gmail.com'
# EMAIL_HOST_PASSWORD = 'urdj jbwg bqzb dmjz'
EMAIL_HOST_PASSWORD = 'joop whjq cxya jwrq'

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
