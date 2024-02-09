from django.urls import path

from .views import CalendarView, TestView, crawler

app_name = 'calendarapp'

urlpatterns = [
    path('', CalendarView.as_view(), name='calendar'),
    path('test', TestView, name='test'),
    path("crawler", crawler, name="crawler"),
]