from django.apps import AppConfig
from coin4u import settings

class NewsappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newsapp'

    def ready(self):
        if settings.local.SCHEDULER_DEFAULT:
            from . import runapscheduler
            runapscheduler.handle()