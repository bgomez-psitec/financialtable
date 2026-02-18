from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings

def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    error = ""
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        error = "Usuario o contraseña inválidos."

    return render(request, "core/login.html", {"error": error})


@login_required(login_url=settings.LOGIN_URL)
def dashboard(request):
    return render(request, "core/dashboard.html")


@login_required(login_url=settings.LOGIN_URL)
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)
