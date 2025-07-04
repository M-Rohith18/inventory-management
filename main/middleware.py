import jwt
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model

User = get_user_model()
class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            request.user = None
            return  # Allow anonymous requests to go through if desired

        token = auth_header.split(' ')[1]

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get('user_id')

            if not user_id:
                return JsonResponse({'detail': 'Invalid token payload'}, status=401)

            user = User.objects.get(id=user_id)
            request.user = user

        except jwt.ExpiredSignatureError:
            return JsonResponse({'detail': 'Token has expired'}, status=401)
        except jwt.DecodeError:
            return JsonResponse({'detail': 'Token is invalid'}, status=401)
        except User.DoesNotExist:
            return JsonResponse({'detail': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'detail': str(e)}, status=400)
