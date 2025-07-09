from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
import jwt
from rest_framework.exceptions import AuthenticationFailed


User = get_user_model()

class JWTAuthenticationMixin:
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationFailed('Authorization header missing or invalid')
            # return None, Response({'detail': 'Authorization header missing or invalid'}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)
            request.user = user 
            return user, None
        except jwt.ExpiredSignatureError:
            return None, Response({'detail': 'Token has expired'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return None, Response({'detail': 'Token is invalid'}, status=status.HTTP_401_UNAUTHORIZED)
        except User.DoesNotExist:
            return None, Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return None, Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
