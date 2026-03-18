from django.conf import settings


def auth_urls(request):
    # Determina si el usuario autenticado es de solo lectura.
    # Staff nunca es readonly independientemente del flag.
    user_is_readonly = False
    if request.user.is_authenticated and not request.user.is_staff:
        try:
            user_is_readonly = request.user.profile.is_readonly
        except Exception:
            user_is_readonly = False

    return {
        "LOGIN_URL": settings.LOGIN_URL,
        "LOGIN_REDIRECT_URL": settings.LOGIN_REDIRECT_URL,
        "APP_VERSION": settings.APP_VERSION,
        "user_is_readonly": user_is_readonly,
    }
