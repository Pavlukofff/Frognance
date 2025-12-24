from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import RegisterForm, ProfileForm
from .services import create_user


def home(request):
    """
    Renders the home page.
    """
    return render(request, 'home.html')


def register(request):
    """
    Handles user registration.

    On GET, it displays the registration form.
    On POST, it validates the form data, creates a new user, and redirects
    to the login page upon successful registration.
    """
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
def edit_profile(request):
    """
    Handles profile editing for a logged-in user.

    On GET, it displays the profile form pre-filled with the user's data.
    On POST, it validates and saves the updated profile information,
    including the avatar image.
    """
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})
