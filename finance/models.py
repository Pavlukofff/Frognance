from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Category(models.Model):
    """
    Represents a category for financial transactions.

    A category can be personal to a user or shared within a group. It can
    also be marked as an income category.
    """
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
        """
        Return the name of the category.
        """
        return self.name


class Transaction(models.Model):
    """
    Represents a financial transaction.

    A transaction can be either an income or an expense. It is associated
    with a user and can optionally belong to a group.
    """
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
    date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'Transaction'
        indexes = [models.Index(fields=['user', 'group'])]

    def __str__(self):
        """
        Return a string representation of the transaction, including its type and amount.
        """
        return f"{self.t_type}: {self.amount}"


class UserGroup(models.Model):
    """
    Represents a group of users for shared financial management.
    """
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_groups'

    def __str__(self):
        """
        Return the name of the group.
        """
        return self.name


class UserGroupMember(models.Model):
    """
    Represents the membership of a user in a group.

    This model links a user to a group and defines their role within it
    (e.g., 'admin' or 'member').
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(UserGroup, on_delete=models.CASCADE, related_name='members')
    role = models.CharField(max_length=20, default='member', choices=[('admin', 'Admin'), ('member', 'Member')])
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_group_members'
        unique_together = ['user', 'group'] # уникальность

    def __str__(self):
        """
        Return a string representation of the group membership.
        """
        return f"{self.user.username} in {self.group.name} ({self.role})"


class Invitation(models.Model):
    """
    Represents an invitation for a user to join a group.

    An invitation has a status ('pending', 'accepted', 'rejected') and
    tracks who sent the invitation and to whom it was sent.
    """
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
        constraints = [
            models.UniqueConstraint(
                fields=['to_user', 'group'],
                condition=models.Q(status='pending'),
                name='unique_pending_invitation'
            )
        ]

    def __str__(self):
        """
        Return a string representation of the invitation.
        """
        return f"Приглашение от {self.from_user} для {self.to_user} в {self.group}"
