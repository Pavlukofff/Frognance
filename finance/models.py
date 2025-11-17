from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Expense(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'Expense'

class Income(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.RESTRICT)

    class Meta:
        db_table = 'Income'