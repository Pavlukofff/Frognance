from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# class Expense(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.RESTRICT)
#
#     class Meta:
#         db_table = 'Expense'

# class Income(models.Model):
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     user = models.ForeignKey(User, on_delete=models.RESTRICT)
#
#     class Meta:
#         db_table = 'Income'

class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'

    )
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=30, blank=True)
    is_income = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TYPE_CHOICES = (
        ('income', 'Доход'),
        ('expense', 'Расход'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    t_type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Transaction'

    def __str__(self):
        return f"{self.t_type}: {self.amount}"
