from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Sum
from openpyxl import Workbook

from finance.forms import RegisterForm, TransactionForm, CategoryForm, UserGroupForm
from finance.models import Transaction, UserGroupMember, UserGroup
from finance.services import create_user


def home(request):
    return render(request, 'home.html')


def login(request):
    return render(request, 'registration/login.html')


def register(request):
    form = RegisterForm

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']

            create_user(username=username, email=email, password=password)

            return redirect(reverse('login'))

    return render(request, 'registration/register.html', {'form': form})


# @login_required
# def create_income_view(request):
#     form = IncomeForm
#
#     if request.method == 'POST':
#         form = IncomeForm(request.POST)
#         if form.is_valid():
#             title = form.cleaned_data['title']
#             content = form.cleaned_data['content']
#
#             income = create_income(title=title, content=content, user=request.user) # пользователь который сделал запрос
#
#             return redirect(reverse('income-view', args=(income.id,)))
#
#     return render(request, 'operation/create_income.html', {'form': form})

# @login_required
# def income_view(request, income_id: int):
#     income = get_object_or_404(Income, id=income_id)
#     if request.user != income.user:
#         return HttpResponseForbidden(content='У вас нет доступа')
#
#     return render(request, 'operation/income.html', {'income': income})

@login_required
def dashboard(request):
    personal_transactions = Transaction.objects.filter(user=request.user, group=None).order_by('-date')
    personal_income = personal_transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
    personal_expense = personal_transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    personal_balance = personal_income - personal_expense

    group_balance = None
    group_income = None
    group_expense = None
    group_transactions = None

    member = UserGroupMember.objects.filter(user=request.user).first()
    if member:
        group_transactions = Transaction.objects.filter(group=member.group).order_by('-date')
        group_income = group_transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
        group_expense = group_transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        group_balance = group_income - group_expense
    else:
        transactions = Transaction.objects.filter(user=request.user).order_by('-date')
        income = transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
        balance = income - expense

    return render(request, 'operation/dashboard.html', {
        'personal_transactions': personal_transactions,
        'personal_income': personal_income,
        'personal_expense': personal_expense,
        'personal_balance': personal_balance,
        'group_transactions': group_transactions,
        'group_income': group_income,
        'group_expense': group_expense,
        'group_balance': group_balance,
        'group': member.group if member else None
    })


@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  # Всегда личный пользователь
            transaction.group = form.cleaned_data['group']  # Group из формы (или None для личной)
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)

    return render(request, 'operation/add_transaction.html', {'form': form})


@login_required
def transaction_detail(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    return render(request, 'operation/transaction_detail.html', {'transaction': transaction})


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('dashboard')
    else:
        form = CategoryForm()

    return render(request, 'operation/add_category.html', {'form': form})

@login_required
def export_operation_to_excel(request):
    wb = Workbook()

    ws_personal = wb.active
    ws_personal.title = "Personal Transactions"
    headers = ['ID', 'Type', 'Amount', 'Category', 'Description', 'Date']
    ws_personal.append(headers)

    # личные транзакции
    personal_transactions = Transaction.objects.filter(user=request.user, group=None)

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

    member = UserGroupMember.objects.filter(user=request.user).first()
    if member:
        ws_group = wb.create_sheet(title="Group Transactions")
        ws_group.append(headers)

        # групповые транзакции
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

@login_required
def create_group(request):
    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            # Создатель — admin
            UserGroupMember.objects.create(user=request.user, group=group, role='admin')
            return redirect('dashboard')
    else:
        form = UserGroupForm()
    return render(request, 'operation/create_group.html', {'form': form})

@login_required
def join_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id)
    if not UserGroupMember.objects.filter(user=request.user, group=group).exists():
        UserGroupMember.objects.create(user=request.user, group=group, role='member')
    return redirect('dashboard')


@login_required
def group_list(request):
    memberships = UserGroupMember.objects.filter(user=request.user).order_by('-joined_at')

    context = {
        'memberships': memberships,
    }
    return render(request, 'operation/group_list.html', context)


@login_required
def leave_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id)

    membership = UserGroupMember.objects.filter(user=request.user, group=group).first()

    if membership:
        membership.delete()
    else:
        return HttpResponse("Вы не состоите в этой группе.")

    return redirect('group_list')


