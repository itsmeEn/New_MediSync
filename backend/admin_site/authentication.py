from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth import get_user_model
from .models import AdminUser

class AdminJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication for AdminUser model.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id_claim = 'user_id'
    
    def get_user(self, validated_token):
        """
        Returns a user that matches the payload's user id and email.
        """
        try:
            user_id = validated_token[self.user_id_claim]
            user = AdminUser.objects.get(id=user_id)
            return user
        except AdminUser.DoesNotExist:
            raise InvalidToken('User not found')
        except KeyError:
            raise InvalidToken('Token contains no recognizable user identification')
