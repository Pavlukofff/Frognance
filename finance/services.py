from django.contrib.auth import get_user_model

# from finance.models import Income

User = get_user_model()

def create_user(username: str, email: str, password: str) -> User:
    User.objects.create_user(username=username, email=email, password=password)


# def create_income(title: str, content: str, user: User) -> Income:
#     return Income.objects.create(title=title, content=content, user=user)