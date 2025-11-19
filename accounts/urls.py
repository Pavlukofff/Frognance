from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import register, edit_profile

urlpatterns = [
    path('register', register, name='register'),  # регистрация
    path('login', LoginView.as_view(), name='login'),  # логин вход
    path('logout', LogoutView.as_view(), name='logout'),  # логин выход
    path('edit-profile/', edit_profile, name='edit_profile'),  # изменение профиля
]
