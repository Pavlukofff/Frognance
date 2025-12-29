import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from finance.forms import TransactionForm, CategoryForm, UserGroupForm, InvitationForm, User, TransactionFilterForm
from finance.models import Transaction, UserGroupMember, UserGroup, Invitation, Category
from finance.services import create_group_and_add_admin, export_transactions, get_personal_balance, get_group_balance, \
    join_group as join_group_service, leave_group as leave_group_service


def home(request):
    """
    Renders the home page or redirects to dashboard if logged in.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


@login_required
def dashboard(request):
    """
    Displays the main dashboard, handles transaction filtering, and prepares chart data.
    """
    # 1. Get all base data (unfiltered)
    personal_transactions_all, personal_income, personal_expense, personal_balance = get_personal_balance(request.user)
    group_transactions_all, group_income, group_expense, group_balance, group = get_group_balance(request.user)

    # 2. Handle filtering form
    filter_form = TransactionFilterForm(request.GET or None, user=request.user)
    personal_transactions_filtered = personal_transactions_all
    group_transactions_filtered = group_transactions_all

    if filter_form.is_valid():
        selected_category = filter_form.cleaned_data.get('category')
        if selected_category:
            personal_transactions_filtered = personal_transactions_all.filter(category=selected_category)
            if group_transactions_filtered:
                group_transactions_filtered = group_transactions_all.filter(category=selected_category)

    # 3. Prepare chart data (always unfiltered)
    expense_by_category = (
        Transaction.objects.filter(user=request.user, t_type='expense', group=None)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )
    chart_labels = [item['category__name'] or 'Uncategorized' for item in expense_by_category]
    chart_data = [float(item['total']) for item in expense_by_category]

    context = {
        # Base data (unfiltered totals)
        'personal_income': personal_income,
        'personal_expense': personal_expense,
        'personal_balance': personal_balance,
        'group_income': group_income,
        'group_expense': group_expense,
        'group_balance': group_balance,
        'group': group,
        # Filtered transaction lists
        'personal_transactions': personal_transactions_filtered,
        'group_transactions': group_transactions_filtered,
        # Chart data
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        # Form
        'filter_form': filter_form,
    }
    return render(request, 'operation/dashboard.html', context)


@login_required
def add_transaction(request):
    """
    Handles the creation of a new financial transaction.
    """
    user_categories = Category.objects.filter(Q(user=request.user) | Q(user=None))
    
    categories_json = json.dumps({
        cat.pk: {'name': cat.name, 'is_income': cat.is_income}
        for cat in user_categories
    })

    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.group = form.cleaned_data.get('group')
            transaction.save()
            return redirect('dashboard')
    else:
        form = TransactionForm(user=request.user)

    context = {
        'form': form,
        'categories_json': categories_json,
    }
    return render(request, 'operation/add_transaction.html', context)


@login_required
def transaction_detail(request, pk):
    """
    Displays the details of a specific transaction.
    """
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    return render(request, 'operation/transaction_detail.html', {'transaction': transaction})


@login_required
def add_category(request):
    """
    Handles the creation of a new category for transactions.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect('add_transaction') # Redirect to transaction page to see the new category
    else:
        form = CategoryForm()

    return render(request, 'operation/add_category.html', {'form': form})


@login_required
def export_operation_to_excel(request):
    """
    Triggers the export of the user's transactions to an Excel file.
    (Placeholder function)
    """
    # This function is currently a placeholder.
    # The actual export logic is in finance.services.export_transactions
    return export_transactions(request.user)


@login_required
def create_group(request):
    """
    Handles the creation of a new user group.
    """
    if request.method == 'POST':
        form = UserGroupForm(request.POST)
        if form.is_valid():
            create_group_and_add_admin(form.cleaned_data['name'], request.user)
            return redirect('dashboard')
    else:
        form = UserGroupForm()
    return render(request, 'group/create_group.html', {'form': form})


@login_required
def join_group(request, group_id):
    """
    Allows a user to join a group directly via a URL.
    """
    join_group_service(request.user, group_id)
    return redirect('dashboard')


@login_required
def group_list(request):
    """
    Displays a list of all groups the current user is a member of.
    """
    memberships = UserGroupMember.objects.filter(user=request.user).order_by('-joined_at')
    context = {
        'memberships': memberships,
    }
    return render(request, 'group/group_list.html', context)


@login_required
def leave_group(request, group_id):
    """
    Handles a user leaving a group.
    """
    success = leave_group_service(request.user, group_id)
    if not success:
        return HttpResponse("You are not a member of this group.")
    return redirect('group_list')


@login_required
def invite_to_group(request, group_id):
    """
    Allows a group admin to invite another user to the group.
    """
    group = get_object_or_404(UserGroup, id=group_id)
    if not UserGroupMember.objects.filter(user=request.user, group=group, role='admin').exists():
        return HttpResponseForbidden("Only admins can invite users.")

    if request.method == 'POST':
        form = InvitationForm(request.POST, group=group)
        if form.is_valid():
            to_username = form.cleaned_data['to_username']
            to_user = get_object_or_404(User, username=to_username)
            Invitation.objects.create(from_user=request.user, to_user=to_user, group=group)
            return redirect('group_list')
    else:
        form = InvitationForm(group=group)

    return render(request, 'group/invite_to_group.html', {'form': form, 'group': group})


@login_required
def invitations_list(request):
    """
    Displays a list of pending group invitations for the current user.
    """
    invitations = Invitation.objects.filter(to_user=request.user, status='pending').order_by('-created_at')
    return render(request, 'group/invitations_list.html', {'invitations': invitations})


@login_required
def accept_invitation(request, invitation_id):
    """
    Handles the acceptance of a group invitation.
    """
    invitation = get_object_or_404(Invitation, id=invitation_id, to_user=request.user)
    if invitation.status != 'pending':
        return HttpResponse("This invitation has already been processed.")

    UserGroupMember.objects.create(user=request.user, group=invitation.group, role='member')
    invitation.status = 'accepted'
    invitation.save()
    return redirect('invitations_list')


@login_required
def reject_invitation(request, invitation_id):
    """
    Handles the rejection of a group invitation.
    """
    invitation = get_object_or_404(Invitation, id=invitation_id, to_user=request.user)
    if invitation.status != 'pending':
        return HttpResponse("This invitation has already been processed.")

    invitation.status = 'rejected'
    invitation.save()
    return redirect('invitations_list')


@login_required
def group_members(request, group_id):
    """
    Displays the list of members for a specific group.
    """
    group = get_object_or_404(UserGroup, id=group_id)
    if not UserGroupMember.objects.filter(user=request.user, group=group).exists():
        return HttpResponseForbidden("You do not have access to this group.")

    members = UserGroupMember.objects.filter(group=group).order_by('role', 'joined_at')
    is_admin = UserGroupMember.objects.filter(user=request.user, group=group, role='admin').exists()

    if request.method == 'POST':
        if not is_admin:
            return HttpResponseForbidden("Only admins can remove members.")
        member_id = request.POST.get('member_id')
        member_to_kick = get_object_or_404(UserGroupMember, id=member_id, group=group)
        if member_to_kick.role == 'admin':
            return HttpResponse("Admins cannot be removed.")
        if member_to_kick.user == request.user:
            return HttpResponse("You cannot remove yourself. Use the 'Leave Group' option.")
        member_to_kick.delete()
        return redirect('group_members', group_id=group_id)

    return render(request, 'group/group_members.html', {
        'group': group,
        'members': members,
        'is_admin': is_admin
    })


@login_required
def income_list(request):
    """
    Displays a list of the user's income transactions and their sum.
    """
    incomes = Transaction.objects.filter(user=request.user, t_type='income').order_by('-date')
    total_income = incomes.aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'operation/income_list.html', {'incomes': incomes, 'total_income': total_income})
