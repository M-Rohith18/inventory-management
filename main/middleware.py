import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            request.user = AnonymousUser()
            return

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)
            request.user = user  # 🔐 User is authenticated
        except jwt.ExpiredSignatureError:
            request.user = AnonymousUser()
        except jwt.DecodeError:
            request.user = AnonymousUser()
        except User.DoesNotExist:
            request.user = AnonymousUser()
        except Exception:
            request.user = AnonymousUser()



