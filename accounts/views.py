from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import RegisterForm, ProfileForm


def home(request):
    """
    Renders the home page for anonymous users or redirects authenticated
    users to their dashboard.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def register(request):
    """
    Handles user registration using a UserCreationForm.

    On GET, it displays the registration form.
    On POST, it validates the form data. If valid, it saves the new user
    and redirects to the login page. If invalid, it re-renders the form
    with validation errors.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()  # This handles user creation and password hashing
            return redirect(reverse('login'))
    else:
        form = RegisterForm()

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
