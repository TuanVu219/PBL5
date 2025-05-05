# your_app/authentication_backend.py

from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from .authentication import decode_access_token

class CustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != b'bearer':
            return None  # Cho phép anonymous access nếu không có token

        if len(auth) != 2:
            raise AuthenticationFailed('Invalid token header.')

        token = auth[1].decode('utf-8')
        user_id = decode_access_token(token)

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')

        return (user, None)
