from django.shortcuts import render, redirect
from django.urls import reverse

from finance.forms import RegisterForm
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
