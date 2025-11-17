from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from finance.models import Income

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput()
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', 'Пароли не совпадают')

        return cleaned_data


class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['title', 'content']