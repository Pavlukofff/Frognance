from django.db.models import Sum, Q
from openpyxl import Workbook
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Transaction, UserGroup, UserGroupMember, User


def get_personal_balance(user: User):
    """
    Calculates the financial balance for a user's personal transactions.

    Args:
        user: The user for whom to calculate the balance.

    Returns:
        A tuple containing:
        - A queryset of personal transactions.
        - The total income.
        - The total expense.
        - The final balance (income - expense).
    """
    transactions = Transaction.objects.filter(user=user, group=None).select_related('category').order_by('-date')
    income = transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return transactions, income, expense, income - expense


def get_group_balance(user: User):
    """
    Calculates the financial balance for the group a user is a member of.

    Args:
        user: The user whose group balance is to be calculated.

    Returns:
        A tuple containing:
        - A queryset of group transactions.
        - The total group income.
        - The total group expense.
        - The final group balance.
        - The group object.
        If the user is not in a group, returns (None, None, None, None, None).
    """
    member = UserGroupMember.objects.filter(user=user).first()
    if not member:
        return None, None, None, None, None
    transactions = Transaction.objects.filter(group=member.group).select_related('category').order_by('-date')
    income = transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return transactions, income, expense, income - expense, member.group


def export_transactions(user: User) -> HttpResponse:
    """
    Exports a user's personal and group transactions to an Excel file.

    Args:
        user: The user whose transactions are to be exported.

    Returns:
        An HttpResponse containing the generated Excel file.
    """
    wb = Workbook()
    ws_personal = wb.active
    ws_personal.title = "Personal Transactions"
    headers = ['ID', 'Type', 'Amount', 'Category', 'Description', 'Date']
    ws_personal.append(headers)

    personal_transactions = Transaction.objects.filter(user=user, group=None).select_related('category')
    for transaction in personal_transactions:
        row = [
            transaction.id,
            transaction.t_type,
            float(transaction.amount),
            transaction.category.name if transaction.category else '',
            transaction.description,
            transaction.date.strftime('%Y-%m-%d'),
        ]
        ws_personal.append(row)

    member = UserGroupMember.objects.filter(user=user).first()
    if member:
        ws_group = wb.create_sheet(title="Group Transactions")
        ws_group.append(headers)

        group_transactions = Transaction.objects.filter(group=member.group).select_related('category')
        for transaction in group_transactions:
            row = [
                transaction.id,
                transaction.t_type,
                float(transaction.amount),
                transaction.category.name if transaction.category else '',
                transaction.description,
                transaction.date.strftime('%Y-%m-%d'),
            ]
            ws_group.append(row)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="transactions.xlsx"'
    wb.save(response)
    return response


def create_group_and_add_admin(name: str, user: User) -> UserGroup:
    """
    Creates a new user group and assigns the creator as an admin.

    Args:
        name: The name of the new group.
        user: The user creating the group.

    Returns:
        The newly created UserGroup object.
    """
    group = UserGroup.objects.create(name=name)
    UserGroupMember.objects.create(user=user, group=group, role='admin')
    return group


def join_group(user: User, group_id: int) -> UserGroup:
    """
    Adds a user to a group as a member.

    Args:
        user: The user to add to the group.
        group_id: The ID of the group to join.

    Returns:
        The UserGroup object that the user joined.
    """
    group = get_object_or_404(UserGroup, id=group_id)
    if not UserGroupMember.objects.filter(user=user, group=group).exists():
        UserGroupMember.objects.create(user=user, group=group, role='member')
    return group


def leave_group(user: User, group_id: int) -> bool:
    """
    Removes a user's membership from a group.

    Args:
        user: The user leaving the group.
        group_id: The ID of the group to leave.

    Returns:
        True if the user was successfully removed, False otherwise.
    """
    group = get_object_or_404(UserGroup, id=group_id)
    membership = UserGroupMember.objects.filter(user=user, group=group).first()
    if membership:
        membership.delete()
        return True
    return False
