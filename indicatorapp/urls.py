from django.urls import path, include
from . import views

app_name = "indicatorapp"

urlpatterns = [
    path("", views.index, name="index"),
    path("crawler/", views.crawler, name="crawler"),
    path('test', views.TestView, name='test'),
]