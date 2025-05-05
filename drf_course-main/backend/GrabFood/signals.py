from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from rest_framework.authtoken.models import Token
from django_celery_beat.models import PeriodicTask, IntervalSchedule
@receiver(post_save, sender=User, weak=False)

def setup_periodic_tasks(sender, **kwargs):
    # Tạo lịch chạy định kỳ nếu chưa tồn tại
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=1,  # Thời gian
        period=IntervalSchedule.MINUTES,  # Đơn vị thời gian
    )

    # Tạo công việc định kỳ
    PeriodicTask.objects.get_or_create(
        interval=schedule,
        name="Delete expired vouchers periodically",
        task="GrabFood.tasks.delete_expired_vouchers",  # Đường dẫn task của bạn
    )