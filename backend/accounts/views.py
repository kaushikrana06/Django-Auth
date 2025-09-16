from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

# ------------ helpers ------------
def set_refresh_cookie(response, refresh_str: str):
    response.set_cookie(
        settings.REFRESH_COOKIE_NAME,
        refresh_str,
        httponly=settings.REFRESH_COOKIE_HTTPONLY,
        secure=settings.REFRESH_COOKIE_SECURE,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
        path=settings.REFRESH_COOKIE_PATH,
        max_age=7 * 24 * 60 * 60,  # match REFRESH lifetime for dev
    )
    return response

def clear_refresh_cookie(response):
    response.delete_cookie(
        settings.REFRESH_COOKIE_NAME,
        path=settings.REFRESH_COOKIE_PATH,
        samesite=settings.REFRESH_COOKIE_SAMESITE,
    )
    return response

# ------------ endpoints ------------

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        email = request.data.get("email", "")

        if not username or not password:
            return Response({"detail": "Username and password required"},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Username already taken"},
                            status=status.HTTP_400_BAD_REQUEST)

        User.objects.create_user(username=username, password=password, email=email)
        return Response({"detail": "User registered successfully"},
                        status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")  # simplify dev CSRF (tighten in prod)
class LoginView(TokenObtainPairView):
    """
    Body: {"username": "...", "password": "..."}
    Returns: {"access": "..."} and sets HttpOnly refresh cookie
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and "refresh" in response.data:
            refresh = response.data.pop("refresh")
            set_refresh_cookie(response, refresh)
        return response


@method_decorator(csrf_exempt, name="dispatch")
class RefreshView(APIView):
    """
    Reads refresh from HttpOnly cookie; returns new access and rotates cookie.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        cookie_refresh = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if not cookie_refresh:
            return Response({"detail": "No refresh cookie"}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = TokenRefreshSerializer(data={"refresh": cookie_refresh})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError:
            return Response({"detail": "Invalid refresh"}, status=status.HTTP_401_UNAUTHORIZED)

        data = serializer.validated_data
        access = data.get("access")
        new_refresh = data.get("refresh")  # present because ROTATE_REFRESH_TOKENS=True

        resp = Response({"access": access})
        if new_refresh:
            set_refresh_cookie(resp, new_refresh)
        return resp


@method_decorator(csrf_exempt, name="dispatch")
class LogoutView(APIView):
    """
    Blacklists refresh token (if valid) and clears the cookie.
    Works even if access token is expired (AllowAny).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_cookie = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        resp = Response({"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
        if refresh_cookie:
            try:
                token = RefreshToken(refresh_cookie)
                token.blacklist()
            except Exception:
                pass
        clear_refresh_cookie(resp)
        return resp


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        u = request.user
        return Response({"id": u.id, "username": u.username})
