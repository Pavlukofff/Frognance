from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories'

    )
    group = models.ForeignKey('UserGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='categories')
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

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey('UserGroup', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='transactions')
    t_type = models.CharField(max_length=7, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Transaction'
        indexes = [models.Index(fields=['user', 'group'])]

    def __str__(self):
        return f"{self.t_type}: {self.amount}"


class UserGroup(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_groups'

    def __str__(self):
        return self.name

# управление членами групп
class UserGroupMember(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, default='member', choices=[('admin', 'Admin'), ('member', 'Member')])
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_group_members'
        unique_together = ['user', 'group'] # уникальность

    def __str__(self): # админка
        return f"{self.user.username} in {self.group.name} ({self.role})"

# приглашения, статусы, история
class Invitation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    )

    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_invitations')
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_invitations')
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='invitations')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'invitations'
        unique_together = ['to_user', 'group']  # нельзя приглашать одного пользователя в группу дважды

    def __str__(self):
        return f"Приглашение от {self.from_user} для {self.to_user} в {self.group}"
