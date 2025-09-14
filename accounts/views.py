from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView


class RegisterView(APIView):
    """
    POST /api/register/
    Body: {"username": "...", "password": "...", "email": "..."}
    Creates a normal user account (not staff, not superuser).
    """
    permission_classes = [permissions.AllowAny]

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

        user = User.objects.create_user(username=username, password=password, email=email)
        return Response({"detail": "User registered successfully"},
                        status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    """
    POST /api/login/
    Body: {"username": "...", "password": "..."}
    Returns: {"access": "..."} and sets HttpOnly cookie with refresh token
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200 and "refresh" in response.data:
            refresh = response.data.pop("refresh")
            response.set_cookie(
                "refresh_token",
                refresh,
                httponly=True,
                secure=False,  # use True with HTTPS in production
                samesite="Lax",
                max_age=7 * 24 * 60 * 60,
            )
        return response


class RefreshView(APIView):
    """
    POST /api/refresh/
    Reads refresh token from cookie and returns new access token
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        if not refresh_token:
            return Response({"detail": "Refresh token missing"}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)
            return Response({"access": access})
        except Exception:
            return Response({"detail": "Invalid or expired refresh token"}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    POST /api/logout/
    Blacklists refresh token + clears cookie
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")
        response = Response({"detail": "Logged out"}, status=status.HTTP_205_RESET_CONTENT)
        response.delete_cookie("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return response
