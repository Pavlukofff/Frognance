from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model that extends the default AbstractUser.

    Adds optional fields for phone number and avatar. The email field is
    required for registration.
    """
    # кастомные поля
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        """
        Return the username as the string representation of the user.
        """
        return self.username  # отображение по username
