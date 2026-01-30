from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailBackEnd(ModelBackend):
    """
    Custom authentication backend that allows users to login using their email address
    instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Use email field for authentication
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Handle edge case where multiple users have the same email
            return None
        else:
            if user.check_password(password):
                return user
        return None
    
    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
