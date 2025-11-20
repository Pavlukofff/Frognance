from django.db.models import Sum
from openpyxl import Workbook
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Transaction, UserGroup, UserGroupMember


def get_personal_balance(user):
    transactions = Transaction.objects.filter(user=user, group=None).order_by('-date')
    income = transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return transactions, income, expense, income - expense


def get_group_balance(user):
    member = UserGroupMember.objects.filter(user=user).first()
    if not member:
        return None, None, None, None, None
    transactions = Transaction.objects.filter(group=member.group).order_by('-date')
    income = transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    return transactions, income, expense, income - expense, member.group

# Excel
def export_transactions(user):
    wb = Workbook()
    ws_personal = wb.active
    ws_personal.title = "Личные операции"
    headers = ['ID', 'Type', 'Amount', 'Category', 'Description', 'Date']
    ws_personal.append(headers)

    personal_transactions = Transaction.objects.filter(user=user, group=None)
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

    member = UserGroupMember.objects.filter(user=user).first() # проверка состояния в группе
    if member:
        ws_group = wb.create_sheet(title="Операции группы")
        ws_group.append(headers)

        group_transactions = Transaction.objects.filter(group=member.group)
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


def create_group_and_add_admin(name, user):
    group = UserGroup.objects.create(name=name)
    UserGroupMember.objects.create(user=user, group=group, role='admin')
    return group


def join_group(user, group_id):
    group = get_object_or_404(UserGroup, id=group_id)
    if not UserGroupMember.objects.filter(user=user, group=group).exists():
        UserGroupMember.objects.create(user=user, group=group, role='member')
    return group


def leave_group(user, group_id):
    group = get_object_or_404(UserGroup, id=group_id)
    membership = UserGroupMember.objects.filter(user=user, group=group).first()
    if membership:
        membership.delete()
        return True
    return False
