"""
URL configuration for frognance project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from finance import views
from finance.views import home, register, export_operation_to_excel

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register', register, name='register'),
    path('login', LoginView.as_view(), name='login'),
    path("logout", LogoutView.as_view(), name='logout'),
    # path('operation/income', create_income_view, name='create-income'),
    # path('operation/<int:income_id>', income_view, name='income-view'),
    path('operation/transaction', views.dashboard, name='dashboard'),
    path('operation/add/', views.add_transaction, name='add_transaction'),
    path('transaction/<int:pk>', views.transaction_detail, name='transaction_detail'),
    path('add-category/', views.add_category, name='add_category'),
    path('export-operation/', export_operation_to_excel, name='export_operation'),
    path('create-group/', views.create_group, name='create_group'),
    path('join-group/<int:group_id>/', views.join_group, name='join_group'),
    path('groups/', views.group_list, name='group_list'),
    path('leave-group/<int:group_id>/', views.leave_group, name='leave_group'),
]


