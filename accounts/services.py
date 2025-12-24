from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(username: str, email: str, password: str) -> User:
    """
    Creates and saves a new user.

    Args:
        username: The username for the new user.
        email: The email address for the new user.
        password: The password for the new user.

    Returns:
        The newly created user object.
    """
    return User.objects.create_user(username=username, email=email, password=password)
