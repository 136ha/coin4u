from django.urls import path

from .views import CalendarView

app_name = 'calendarapp'

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'),

]