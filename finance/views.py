from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum

from finance.forms import TransactionForm, CategoryForm, UserGroupForm, InvitationForm, User
from finance.models import Transaction, UserGroupMember, UserGroup, Invitation
from finance.services import create_group_and_add_admin, export_transactions, get_personal_balance, get_group_balance


def home(request):
    return render(request, 'home.html')


# личный/групповой баланс, списки операций
@login_required
def dashboard(request):
    personal_transactions, personal_income, personal_expense, personal_balance = get_personal_balance(request.user)
    group_transactions, group_income, group_expense, group_balance, group = get_group_balance(request.user)
    context = {
        'personal_transactions': personal_transactions,
        'personal_income': personal_income,
        'personal_expense': personal_expense,
        'personal_balance': personal_balance,
        'group_transactions': group_transactions,
        'group_income': group_income,
        'group_expense': group_expense,
        'group_balance': group_balance,
        'group': group
    }
    return render(request, 'operation/dashboard.html', context)


# добавляет операци.
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user  # личный пользователь
            transaction.group = form.cleaned_data['group']  # group из формы или None для личной
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)

    return render(request, 'operation/add_transaction.html', {'form': form})


# просмотр операции
@login_required
def transaction_detail(request, pk):
    transaction = Transaction.objects.get(pk=pk, user=request.user)
    return render(request, 'operation/transaction_detail.html', {'transaction': transaction})


# добавление категории
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('dashboard')
    else:
        form = CategoryForm()

    return render(request, 'operation/add_category.html', {'form': form})


# экспорт в exel
@login_required
def export_operation_to_excel(request):
    return export_transactions(request.user)


# создание групп
@login_required
def create_group(request):
    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():
            create_group_and_add_admin(form.cleaned_data['name'], request.user)
            return redirect('dashboard')
    else:
        form = UserGroupForm()
    return render(request, 'group/create_group.html', {'form': form})


# присоединение к группе
@login_required
def join_group(request, group_id):
    join_group(request.user, group_id)
    return redirect('dashboard')


# список групп
@login_required
def group_list(request):
    memberships = UserGroupMember.objects.filter(user=request.user).order_by('-joined_at')

    context = {
        'memberships': memberships,
    }
    return render(request, 'group/group_list.html', context)


# покинуть группу
@login_required
def leave_group(request, group_id):
    success = leave_group(request.user, group_id)
    if not success:
        return HttpResponse("Вы не состоите в этой группе.")
    return redirect('group_list')


# приглашение в группу
@login_required
def invite_to_group(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id)
    membership = UserGroupMember.objects.filter(user=request.user, group=group, role='admin').first()
    if not membership:
        return HttpResponseForbidden("Только админ может приглашать.")

    if request.method == 'POST':
        form = InvitationForm(request.POST, group=group)
        if form.is_valid():
            to_username = form.cleaned_data['to_username']
            to_user = User.objects.get(username=to_username)
            Invitation.objects.create(from_user=request.user, to_user=to_user, group=group)
            return redirect('group_list')
    else:
        form = InvitationForm(group=group)

    return render(request, 'group/invite_to_group.html', {'form': form, 'group': group})


# список приглашенйи в группу
@login_required
def invitations_list(request):
    invitations = Invitation.objects.filter(to_user=request.user, status='pending').order_by('-created_at')
    return render(request, 'group/invitations_list.html', {'invitations': invitations})


# приглашение
@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, to_user=request.user)
    if invitation.status != 'pending':
        return HttpResponse("Приглашение уже обработано.")

    UserGroupMember.objects.create(user=request.user, group=invitation.group, role='member')
    invitation.status = 'accepted'
    invitation.save()
    return redirect('invitations_list')


@login_required
def reject_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, to_user=request.user)
    if invitation.status != 'pending':
        return HttpResponse("Приглашение уже обработано.")

    invitation.status = 'rejected'
    invitation.save()
    return redirect('invitations_list')


# члены группы
@login_required
def group_members(request, group_id):
    group = get_object_or_404(UserGroup, id=group_id)
    # проверка пользователя в группе
    if not UserGroupMember.objects.filter(user=request.user, group=group).exists():
        return HttpResponseForbidden("У вас нет доступа к этой группе.")

    members = UserGroupMember.objects.filter(group=group).order_by('role', 'joined_at')
    is_admin = UserGroupMember.objects.filter(user=request.user, group=group, role='admin').exists()

    if request.method == 'POST':
        if not is_admin:
            return HttpResponseForbidden("Только админ может удалять членов.")
        member_id = request.POST.get('member_id')
        member_to_kick = get_object_or_404(UserGroupMember, id=member_id, group=group)
        if member_to_kick.role == 'admin':
            return HttpResponse("Нельзя удалить админа группы.")
        if member_to_kick.user == request.user:
            return HttpResponse("Нельзя удалить себя — используйте 'Покинуть'.")
        member_to_kick.delete()
        return redirect('group_members', group_id=group_id)

    return render(request, 'group/group_members.html', {
        'group': group,
        'members': members,
        'is_admin': is_admin
    })


# список доходов
@login_required
def income_list(request):
    incomes = Transaction.objects.filter(user=request.user, t_type='income').order_by('-date')
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'operation/income_list.html', {'incomes': incomes, 'total_income': total_income})
