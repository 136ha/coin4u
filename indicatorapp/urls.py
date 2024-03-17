from django.urls import path, include
from . import views

app_name = "indicatorapp"

urlpatterns = [
    path("", views.indexView, name="index"),
    path('detail/', views.detailView, name="detail"),
    path('error/', views.detailView, name="error"),
    path("crawler/", views.crawler, name="crawler"),
    # path('test', views.TestView, name='test'),
]