from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Đặt biến môi trường Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PBL5.settings')

# Tạo ứng dụng Celery
app = Celery('PBL5')

# Đọc cấu hình từ Django settings, sử dụng namespace 'CELERY'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động tìm và nạp các task từ các ứng dụng đã cài
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
