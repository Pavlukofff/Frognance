from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Sum

from finance.forms import RegisterForm, TransactionForm, CategoryForm
from finance.models import Transaction
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
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    income = transactions.filter(t_type='income').aggregate(total=Sum('amount'))['total'] or 0
    expense = transactions.filter(t_type='expense').aggregate(total=Sum('amount'))['total'] or 0
    balance = income - expense

    return render(request, 'operation/dashboard.html', {
        'transactions': transactions,
        'income': income,
        'expense': expense,
        'balance': balance
    })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('home')

    else:
        form = TransactionForm(user=request.user)

    return render(request, 'operation/add_transaction.html', {'form': form})

def transaction_detail(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    return render(request, 'operation/transaction_detail.html', {'transaction': transaction})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user  # связываем категорию с пользователем
            category.save()
            return redirect('dashboard')  # или куда нужно
    else:
        form = CategoryForm()

    return render(request, 'operation/add_category.html', {'form': form})