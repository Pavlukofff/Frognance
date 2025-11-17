from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from finance.forms import RegisterForm, IncomeForm
from finance.models import Income
from finance.services import create_user, create_income


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

@login_required
def create_income_view(request):
    form = IncomeForm

    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            income = create_income(title=title, content=content, user=request.user) # пользователь который сделал запрос

            return redirect(reverse('income-view', args=(income.id,)))

    return render(request, 'operation/create_income.html', {'form': form})

@login_required
def income_view(request, income_id: int):
    income = get_object_or_404(Income, id=income_id)
    if request.user != income.user:
        return HttpResponseForbidden(content='У вас нет доступа')

    return render(request, 'operation/income.html', {'income': income})

