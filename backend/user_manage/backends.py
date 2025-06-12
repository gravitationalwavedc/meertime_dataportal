from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend, ModelBackend


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address
    instead of username.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None or password is None:
            return None

        try:
            # Try to find user by email first
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            UserModel().set_password(password)
            return None
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user

        return None


class BearerTokenAuthentication(BaseBackend):
    """
    Bearer Token Authentication Backend for Django
    Provides authentication using Bearer tokens in the Authorization header
    """

    def authenticate(self, request, token=None, **kwargs):
        """
        Authenticate user using Bearer token
        """
        if not token:
            return None

        try:
            from .models import ApiToken

            api_token = ApiToken.objects.select_related("user").get(key=token, is_active=True)

            if api_token.is_expired():
                return None

            # Update last used timestamp
            api_token.update_last_used()

            return api_token.user

        except ApiToken.DoesNotExist:
            return None
        except Exception:
            return None

    def get_user(self, user_id):
        """
        Get user by ID for session management
        """
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
