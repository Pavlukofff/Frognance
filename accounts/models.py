from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # кастомные поля
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username  # отображение по username
