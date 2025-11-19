from django.urls import path
from .views import dashboard, add_transaction, transaction_detail, add_category, export_operation_to_excel, \
    create_group, join_group, group_list, leave_group, invite_to_group, invitations_list, accept_invitation, \
    reject_invitation, group_members, income_list

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('add_transaction/', add_transaction, name='add_transaction'),
    path('transaction/<int:pk>', transaction_detail, name='transaction_detail'),
    path('add_category/', add_category, name='add_category'),
    path('export_operation/', export_operation_to_excel, name='export_operation'),
    path('create_group/', create_group, name='create_group'),
    path('join_group/<int:group_id>/', join_group, name='join_group'),
    path('group_list/', group_list, name='group_list'),
    path('leave_group/<int:group_id>/', leave_group, name='leave_group'),
    path('invite_group/<int:group_id>/', invite_to_group, name='invite_to_group'),
    path('invitations_list/', invitations_list, name='invitations_list'),
    path('accept_invitation/<int:invitation_id>/', accept_invitation, name='accept_invitation'),
    path('reject_invitation/<int:invitation_id>/', reject_invitation, name='reject_invitation'),
    path('group_members/<int:group_id>/', group_members, name='group_members'),
    path('income_list/', income_list, name='income_list'),
]
