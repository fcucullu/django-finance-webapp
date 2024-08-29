import uuid
from django.utils import timezone
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from six import text_type
from .models import UserToken

class AppTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (text_type(user.is_active) + text_type(user.pk) + text_type(timestamp))
    
    def generate_token(self, user):
        token = super().make_token(user)
        UserToken.objects.create(user=user, token=token)
        return token

    def check_token(self, user, token):
        try:
            # Check if the token exists and is not used
            user_token = UserToken.objects.get(user=user, token=token, used=False)
            # Mark the token as used
            user_token.used = True
            user_token.save()
            return True
        except UserToken.DoesNotExist:
            return False

token_generator = AppTokenGenerator()
