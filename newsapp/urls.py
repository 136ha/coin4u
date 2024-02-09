# urls.py
from django.urls import path
from . import views
from .views import crawler

app_name = "newsapp"

urlpatterns = [
    path('', views.NewsView.as_view(), name='index'),
    path("crawler", crawler, name="crawler"),
] 

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)