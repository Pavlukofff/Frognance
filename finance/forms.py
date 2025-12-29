from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from finance.models import Transaction, Category, UserGroup, UserGroupMember, Invitation

User = get_user_model()


class TransactionForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=UserGroup.objects.none(),
        required=False,
        empty_label="Personal Transaction (no group)"
    )

    class Meta:
        model = Transaction
        fields = ['t_type', 'amount', 'category', 'description', 'group']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        # Filter categories to show user's own categories AND global categories
        self.fields['category'].queryset = Category.objects.filter(
            Q(user=user) | Q(user=None)
        )
        self.fields['group'].queryset = UserGroup.objects.filter(members__user=user)

    def clean(self):
        cleaned_data = super().clean()
        t_type = cleaned_data.get('t_type')
        category = cleaned_data.get('category')

        if t_type and category:
            is_income_type = (t_type == 'income')
            if category.is_income != is_income_type:
                self.add_error('category', "Please select a valid category for the chosen transaction type.")
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_income']


class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ['name']


class InvitationForm(forms.Form):
    to_username = forms.CharField(label='Username to invite', max_length=150)

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)

    def clean_to_username(self):
        username = self.cleaned_data['to_username']
        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('User with this username does not exist.')
        if UserGroupMember.objects.filter(user=to_user, group=self.group).exists():
            raise forms.ValidationError('This user is already in the group.')
        if Invitation.objects.filter(to_user=to_user, group=self.group, status='pending').exists():
            raise forms.ValidationError('An invitation has already been sent.')
        return username


class TransactionFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.none(),
        required=False,
        label="Filter by Category"
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(
            Q(user=user) | Q(user=None)
        )
