from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Profile(models.Model):
    # 1대1 마크 되어져 있는 계정이 delete 될 때, profile은 어떻게 될 것인지를 on_delete로 설정
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    image = models.ImageField(upload_to='profile/', null=True)
    nickname = models.CharField(max_length=20, unique=True, null=True)
    message = models.CharField(max_length=100, null=True)