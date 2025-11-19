from django import forms
from django.contrib.auth import get_user_model

from finance.models import Transaction, Category, UserGroup, UserGroupMember, Invitation

User = get_user_model()


# транзакция пользователя
class TransactionForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=UserGroup.objects.none(),  # в __init__
        required=False,
        empty_label="Личная транзакция (без группы)"
    )

    class Meta:
        model = Transaction
        fields = ['t_type', 'amount', 'category', 'description', 'group']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(user=user)

        self.fields['group'].queryset = UserGroup.objects.filter(members__user=user)


# категории
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


# группы пользователя
class UserGroupForm(forms.ModelForm):
    class Meta:
        model = UserGroup
        fields = ['name']


# приглашение в группы
class InvitationForm(forms.Form):
    to_username = forms.CharField(label='Имя пользователя для приглашения', max_length=150)

    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', None)  # группа от view
        super().__init__(*args, **kwargs)

    def clean_to_username(self):
        username = self.cleaned_data['to_username']
        try:
            to_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError('Пользователь с таким именем не существует.')
        if UserGroupMember.objects.filter(user=to_user, group=self.group).exists():
            raise forms.ValidationError('Этот пользователь уже в группе.')
        if Invitation.objects.filter(to_user=to_user, group=self.group, status='pending').exists():
            raise forms.ValidationError('Приглашение уже отправлено.')
        return username
