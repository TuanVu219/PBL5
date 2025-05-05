from django.apps import AppConfig
from django.db.models.signals import post_migrate

class GrabFoodConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'GrabFood'

    def ready(self):
        from .signals import setup_periodic_tasks
        post_migrate.connect(setup_periodic_tasks, sender=self)
