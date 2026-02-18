from django.conf import settings


def auth_urls(request):
    return {
        "LOGIN_URL": settings.LOGIN_URL,
        "LOGIN_REDIRECT_URL": settings.LOGIN_REDIRECT_URL,
    }
