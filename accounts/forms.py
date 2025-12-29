from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    A form for user registration that extends Django's UserCreationForm.

    Includes fields for username, email, and password with confirmation.
    The email field is made required.
    """
    email = forms.EmailField(
        label="Email",
        help_text="Required. A valid email address.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


class ProfileForm(forms.ModelForm):
    """
    A form for editing a user's profile information.
    """
    class Meta:
        model = User
        fields = ['phone', 'avatar']
