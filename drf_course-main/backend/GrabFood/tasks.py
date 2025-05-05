from celery import shared_task
from .models import Voucher
from django.utils.timezone import now
from datetime import datetime

@shared_task
def delete_expired_vouchers():
    expired_vouchers=Voucher.objects.filter(expiration_date__lt=now())
    count=expired_vouchers.count()
    expired_vouchers.delete()
    return f"Deleted {count} expired vouchers."
