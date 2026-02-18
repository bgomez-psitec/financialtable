from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404

from .forms import UserCreateForm, UserUpdateForm

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
    return render(request, "core/dashboard.html", {"active_page": "dashboard"})


@login_required(login_url=settings.LOGIN_URL)
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="dashboard")
def users(request):
    users = User.objects.order_by("username")
    return render(
        request,
        "core/users.html",
        {"users": users, "active_page": "users"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="dashboard")
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("users"))
    else:
        form = UserCreateForm()

    return render(
        request,
        "core/user_form.html",
        {"form": form, "active_page": "users", "title": "Crear usuario"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="dashboard")
def user_edit(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save()
            if request.user.pk == updated_user.pk and form.cleaned_data.get("password1"):
                update_session_auth_hash(request, updated_user)
            return HttpResponseRedirect(reverse("users"))
    else:
        form = UserUpdateForm(instance=user)

    return render(
        request,
        "core/user_form.html",
        {"form": form, "active_page": "users", "title": "Editar usuario"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="dashboard")
def user_delete(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if request.method == "POST":
        user.delete()
        return HttpResponseRedirect(reverse("users"))

    return render(
        request,
        "core/user_confirm_delete.html",
        {"user": user, "active_page": "users"},
    )
