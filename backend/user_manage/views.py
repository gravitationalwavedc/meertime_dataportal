import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_POST


@ensure_csrf_cookie
def get_csrf(request):
    """
    This view is used to get a CSRF token.
    This should be called before any login attempt.
    """
    token = get_token(request)
    return JsonResponse({"csrfToken": token})


@require_POST
@csrf_protect
def login_view(request):
    """
    Login view for Django session authentication
    Accepts email and password via POST
    """
    data = json.loads(request.body)
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return JsonResponse({"detail": "Please provide email and password."}, status=400)

    user = authenticate(request, username=email, password=password)

    if user is None:
        return JsonResponse({"detail": "Invalid credentials."}, status=400)

    login(request, user)

    return JsonResponse(
        {
            "user": {
                "username": user.username,
                "email": user.email,
                "isStaff": user.is_staff,
                "isUnrestricted": user.is_unrestricted(),
            },
            "detail": "Successfully logged in.",
        }
    )


def logout_view(request):
    """
    Logout view for Django session authentication
    """
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "You are not logged in."}, status=400)

    logout(request)

    return JsonResponse({"detail": "Successfully logged out."})


def session_user(request):
    """
    View to check if the user is authenticated and return user info
    """
    if request.user.is_authenticated:
        return JsonResponse(
            {
                "isAuthenticated": True,
                "user": {
                    "username": request.user.username,
                    "email": request.user.email,
                    "isStaff": request.user.is_staff,
                    "isUnrestricted": request.user.is_unrestricted(),
                },
            }
        )
    return JsonResponse({"isAuthenticated": False})
