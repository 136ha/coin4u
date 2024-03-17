from django.apps import AppConfig
from coin4u import settings

class CalendarappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'calendarapp'

    def ready(self):
        if settings.local.SCHEDULER_DEFAULT:
            from . import runapscheduler
            runapscheduler.handle()
