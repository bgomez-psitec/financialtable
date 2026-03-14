from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from decimal import Decimal, InvalidOperation
import csv
import datetime as dt
import io
import random
import string
import unicodedata
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .forms import CompanyInvestmentForm, SMTPConfigForm, SectorForm, UserCreateForm, UserUpdateForm
from .models import (
    CompanyInvestment, Estadio, Fondo, FondoMiembroEquipo,
    IndustrialSector, IndustrialSubSector,
    SMTPConfig, Sector, TechSector, TechSubSector, VerticalClasification,
)

# ── Tablas de referencia (lookup tables) ─────────────────────────────────────
# Cada entrada: (key, label, Model, has_orden)
_REF_TABLES = [
    ("sector",               "Sectores",                    Sector,               False),
    ("fondo",                "Fondos de inversión",         Fondo,                True),
    ("fondo_miembro",        "Miembros de equipo del fondo", FondoMiembroEquipo,  True),
    ("estadio",              "Estadios de inversión",       Estadio,              True),
    ("tech_sector",          "Tech Sectors",                TechSector,           True),
    ("tech_subsector",       "Tech Subsectors",             TechSubSector,        True),
    ("industrial_sector",    "Industrial Sectors",          IndustrialSector,     True),
    ("industrial_subsector", "Industrial Subsectors",       IndustrialSubSector,  True),
    ("vertical",             "Vertical Classifications",    VerticalClasification, True),
]
_REF_TABLE_MAP = {key: (label, Model, has_orden) for key, label, Model, has_orden in _REF_TABLES}


def _companies_for_user(user):
    if user.is_staff:
        return CompanyInvestment.objects.order_by("gd_sociedad")
    return (
        CompanyInvestment.objects.filter(user_links__user=user)
        .distinct()
        .order_by("gd_sociedad")
    )

# ── 2FA helpers ──────────────────────────────────────────────────────────────
_2FA_CODE_LENGTH  = 6
_2FA_EXPIRY_MINS  = 10
_2FA_MAX_ATTEMPTS = 5


def _mask_email(email):
    """Enmascara un email para mostrarlo: ju***@ejemplo.com"""
    if not email or "@" not in email:
        return email
    local, domain = email.split("@", 1)
    visible = min(2, len(local))
    return local[:visible] + "*" * max(0, len(local) - visible) + "@" + domain


def _get_smtp():
    return SMTPConfig.objects.filter(pk=1).first()


def _build_smtp_backend(smtp):
    from django.core.mail.backends.smtp import EmailBackend
    return EmailBackend(
        host=smtp.host,
        port=smtp.port,
        username=smtp.username,
        password=smtp.password,
        use_tls=smtp.use_tls,
        use_ssl=smtp.use_ssl,
        timeout=10,
        fail_silently=False,
    )


def _smtp_from_addr(smtp):
    if smtp.from_name and smtp.from_email:
        return f"{smtp.from_name} <{smtp.from_email}>"
    return smtp.from_email or smtp.username


def _send_2fa_email(smtp, to_email, code):
    from django.core.mail import EmailMessage
    msg = EmailMessage(
        subject="Código de verificación – DataContaBL",
        body=(
            f"Tu código de verificación es:\n\n"
            f"    {code}\n\n"
            f"Este código es válido durante {_2FA_EXPIRY_MINS} minutos.\n"
            f"Si no has iniciado sesión en DataContaBL, ignora este mensaje."
        ),
        from_email=_smtp_from_addr(smtp),
        to=[to_email],
        connection=_build_smtp_backend(smtp),
    )
    msg.send()


def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    # Al volver a la pantalla de login, limpiar cualquier sesión 2FA pendiente
    if request.method == "GET":
        request.session.pop("pending_2fa", None)

    error = ""
    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""
        user = authenticate(request, username=username, password=password)
        if user is not None:
            smtp = _get_smtp()
            if smtp and smtp.host and user.email:
                # 2FA: generar código y enviarlo por email
                code = "".join(random.choices(string.digits, k=_2FA_CODE_LENGTH))
                expires = timezone.now() + dt.timedelta(minutes=_2FA_EXPIRY_MINS)
                request.session["pending_2fa"] = {
                    "user_id": user.pk,
                    "code": code,
                    "expires": expires.isoformat(),
                    "attempts": 0,
                    "email": user.email,
                }
                try:
                    _send_2fa_email(smtp, user.email, code)
                    return HttpResponseRedirect(reverse("verify_2fa"))
                except Exception:
                    request.session.pop("pending_2fa", None)
                    error = (
                        f"No se pudo enviar el código de verificación a "
                        f"{_mask_email(user.email)}. "
                        f"Contacta con el administrador."
                    )
            else:
                # Sin SMTP configurado o el usuario no tiene email → login directo
                login(request, user)
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        else:
            error = "Usuario o contraseña inválidos."

    return render(request, "core/login.html", {"error": error})


def verify_2fa(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

    pending = request.session.get("pending_2fa")
    if not pending:
        return HttpResponseRedirect(reverse("home"))

    def _is_expired():
        expires_dt = dt.datetime.fromisoformat(pending["expires"])
        return timezone.now() > expires_dt

    error = ""
    resend_ok = False

    if request.method == "POST":
        action = request.POST.get("action", "verify")

        # ── Reenviar código ──────────────────────────────────────────────────
        if action == "resend":
            if _is_expired():
                request.session.pop("pending_2fa", None)
                return render(request, "core/verify_2fa.html", {
                    "error": "El código ha expirado. Vuelve a iniciar sesión.",
                    "expired": True,
                })
            smtp = _get_smtp()
            if not smtp or not smtp.host:
                error = "La configuración SMTP no está disponible. Contacta con el administrador."
            else:
                try:
                    new_code = "".join(random.choices(string.digits, k=_2FA_CODE_LENGTH))
                    new_expires = timezone.now() + dt.timedelta(minutes=_2FA_EXPIRY_MINS)
                    pending.update({"code": new_code, "expires": new_expires.isoformat(), "attempts": 0})
                    request.session["pending_2fa"] = pending
                    request.session.modified = True
                    _send_2fa_email(smtp, pending.get("email", ""), new_code)
                    resend_ok = True
                except Exception as exc:
                    error = f"No se pudo reenviar el código: {exc}"

        # ── Verificar código ─────────────────────────────────────────────────
        else:
            # Demasiados intentos previos
            if pending.get("attempts", 0) >= _2FA_MAX_ATTEMPTS:
                request.session.pop("pending_2fa", None)
                return render(request, "core/verify_2fa.html", {
                    "error": "Demasiados intentos incorrectos. Vuelve a iniciar sesión.",
                    "blocked": True,
                })
            # Código expirado
            if _is_expired():
                request.session.pop("pending_2fa", None)
                return render(request, "core/verify_2fa.html", {
                    "error": "El código ha expirado. Vuelve a iniciar sesión.",
                    "expired": True,
                })

            entered = (request.POST.get("code") or "").strip()
            if entered == pending["code"]:
                user = User.objects.get(pk=pending["user_id"])
                request.session.pop("pending_2fa", None)
                login(request, user)
                return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
            else:
                pending["attempts"] = pending.get("attempts", 0) + 1
                request.session["pending_2fa"] = pending
                request.session.modified = True
                remaining = _2FA_MAX_ATTEMPTS - pending["attempts"]
                if remaining <= 0:
                    request.session.pop("pending_2fa", None)
                    return render(request, "core/verify_2fa.html", {
                        "error": "Demasiados intentos incorrectos. Vuelve a iniciar sesión.",
                        "blocked": True,
                    })
                error = f"Código incorrecto. Te quedan {remaining} intento{'s' if remaining != 1 else ''}."

    return render(request, "core/verify_2fa.html", {
        "masked_email": _mask_email(pending.get("email", "")),
        "error": error,
        "resend_ok": resend_ok,
    })


@login_required(login_url=settings.LOGIN_URL)
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGOUT_REDIRECT_URL)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def users(request):
    all_users = User.objects.order_by("username")
    invited   = request.GET.get("invited")   == "1"
    created   = request.GET.get("created")   == "1"
    reinvited = request.GET.get("reinvited") == "1"
    return render(
        request,
        "core/users.html",
        {"users": all_users, "active_page": "users", "invited": invited, "created": created, "reinvited": reinvited},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def user_create(request):
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            # Capturamos la contraseña en texto plano antes de hashearla
            plain_password = form.cleaned_data.get("password1", "")
            new_user = form.save()
            # Guardar temporalmente en sesión para incluirla en el email de invitación
            request.session["invite_password"] = plain_password
            return HttpResponseRedirect(reverse("user_invite", args=[new_user.pk]))
    else:
        form = UserCreateForm()

    return render(
        request,
        "core/user_form.html",
        {"form": form, "active_page": "users", "title": "Crear usuario"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def user_invite(request, user_id):
    """Pantalla de envío de email de invitación tras crear un usuario."""
    invited_user = get_object_or_404(User, pk=user_id)
    smtp = _get_smtp()
    has_smtp = bool(smtp and smtp.host)
    has_email = bool(invited_user.email)

    if request.method == "POST":
        action = request.POST.get("action", "send")

        from_creation = "invite_password" in request.session

        if action == "skip":
            request.session.pop("invite_password", None)
            suffix = "?created=1" if from_creation else ""
            return HttpResponseRedirect(reverse("users") + suffix)

        # action == "send"
        recipient   = (request.POST.get("to_email") or "").strip()
        subject     = (request.POST.get("subject")  or "").strip()
        body        = (request.POST.get("body")     or "").strip()
        send_error  = None

        if not has_smtp:
            send_error = "No hay configuración SMTP disponible."
        elif not recipient:
            send_error = "El destinatario no puede estar vacío."
        else:
            try:
                from django.core.mail import EmailMessage
                msg = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=_smtp_from_addr(smtp),
                    to=[recipient],
                    connection=_build_smtp_backend(smtp),
                )
                msg.send()
                request.session.pop("invite_password", None)
                suffix = "?invited=1" if from_creation else "?reinvited=1"
                return HttpResponseRedirect(reverse("users") + suffix)
            except Exception as exc:
                send_error = f"Error al enviar: {exc}"

        return render(request, "core/user_invite.html", {
            "invited_user": invited_user,
            "has_smtp": has_smtp,
            "has_email": has_email,
            "active_page": "users",
            "send_error": send_error,
            "to_email": recipient,
            "subject": subject,
            "body": body,
        })

    # ── GET: preparar valores por defecto ────────────────────────────────────
    plain_password = request.session.get("invite_password", "")
    site_url = request.build_absolute_uri("/")
    display_name = (
        f"{invited_user.first_name} {invited_user.last_name}".strip()
        or invited_user.username
    )
    default_subject = f"Bienvenido/a a DataContaBL — {display_name}"
    password_line = f"  Contraseña:  {plain_password}\n" if plain_password else ""
    default_body = (
        f"Hola {display_name},\n\n"
        f"Has sido registrado/a en DataContaBL.\n"
        f"A continuación te enviamos tus datos de acceso:\n\n"
        f"  Usuario:     {invited_user.username}\n"
        f"{password_line}"
        f"  Plataforma:  {site_url}\n\n"
        f"Si tienes cualquier pregunta no dudes en contactar con el administrador.\n\n"
        f"Saludos,\n"
        f"El equipo de DataContaBL"
    )

    return render(request, "core/user_invite.html", {
        "invited_user": invited_user,
        "has_smtp": has_smtp,
        "has_email": has_email,
        "active_page": "users",
        "to_email": invited_user.email,
        "subject": default_subject,
        "body": default_body,
    })


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
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
@user_passes_test(lambda u: u.is_staff, login_url="companies")
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


@login_required(login_url=settings.LOGIN_URL)
def companies(request):
    all_companies = _companies_for_user(request.user)
    company_invited = request.GET.get("company_invited") == "1"
    return render(
        request,
        "core/companies.html",
        {"companies": all_companies, "active_page": "companies", "company_invited": company_invited},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def company_invite(request, company_id):
    """Pantalla de envío de email de invitación al CEO de una empresa."""
    company = get_object_or_404(CompanyInvestment, pk=company_id)
    smtp = _get_smtp()
    has_smtp = bool(smtp and smtp.host)
    has_email = bool(company.gd_email_ceo)

    if request.method == "POST":
        action = request.POST.get("action", "send")

        if action == "cancel":
            return HttpResponseRedirect(reverse("companies"))

        # action == "send"
        recipient  = (request.POST.get("to_email") or "").strip()
        subject    = (request.POST.get("subject")  or "").strip()
        body       = (request.POST.get("body")     or "").strip()
        send_error = None

        if not has_smtp:
            send_error = "No hay configuración SMTP disponible."
        elif not recipient:
            send_error = "El destinatario no puede estar vacío."
        else:
            try:
                from django.core.mail import EmailMessage
                msg = EmailMessage(
                    subject=subject,
                    body=body,
                    from_email=_smtp_from_addr(smtp),
                    to=[recipient],
                    connection=_build_smtp_backend(smtp),
                )
                msg.send()
                return HttpResponseRedirect(reverse("companies") + "?company_invited=1")
            except Exception as exc:
                send_error = f"Error al enviar: {exc}"

        return render(request, "core/company_invite.html", {
            "company": company,
            "has_smtp": has_smtp,
            "has_email": has_email,
            "active_page": "companies",
            "send_error": send_error,
            "to_email": recipient,
            "subject": subject,
            "body": body,
        })

    # ── GET: preparar valores por defecto ────────────────────────────────────
    site_url    = request.build_absolute_uri("/")
    ceo_name    = company.gd_ceo or "Sr./Sra."
    company_name = company.gd_sociedad

    default_subject = f"Invitación a completar información — {company_name}"
    default_body = (
        f"Estimado/a {ceo_name},\n\n"
        f"Nos ponemos en contacto con usted en representación de DataContaBL.\n\n"
        f"Estamos actualizando nuestra base de datos de empresas participadas y nos gustaría "
        f"invitarle a completar o actualizar la información correspondiente a {company_name}.\n\n"
        f"Si desea enviarnos la información actualizada o tiene cualquier consulta, "
        f"puede responder directamente a este correo o acceder a nuestra plataforma:\n\n"
        f"  {site_url}\n\n"
        f"Agradecemos de antemano su colaboración.\n\n"
        f"Saludos cordiales,\n"
        f"El equipo de DataContaBL"
    )

    return render(request, "core/company_invite.html", {
        "company": company,
        "has_smtp": has_smtp,
        "has_email": has_email,
        "active_page": "companies",
        "to_email": company.gd_email_ceo,
        "subject": default_subject,
        "body": default_body,
    })


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def company_create(request):
    if request.method == "POST":
        form = CompanyInvestmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("companies"))
    else:
        form = CompanyInvestmentForm()

    return render(
        request,
        "core/company_form.html",
        {"form": form, "active_page": "companies", "title": "Crear empresa"},
    )


@login_required(login_url=settings.LOGIN_URL)
def company_edit(request, company_id):
    if request.user.is_staff:
        company = get_object_or_404(CompanyInvestment, pk=company_id)
    else:
        company = get_object_or_404(
            CompanyInvestment.objects.filter(user_links__user=request.user).distinct(),
            pk=company_id,
        )
    if request.method == "POST":
        form = CompanyInvestmentForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("companies"))
    else:
        form = CompanyInvestmentForm(instance=company)

    return render(
        request,
        "core/company_form.html",
        {"form": form, "active_page": "companies", "title": "Editar empresa"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def company_delete(request, company_id):
    company = get_object_or_404(CompanyInvestment, pk=company_id)
    if request.method == "POST":
        company.delete()
        return HttpResponseRedirect(reverse("companies"))

    return render(
        request,
        "core/company_confirm_delete.html",
        {"company": company, "active_page": "companies"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def company_import(request):
    errors = []
    imported = 0
    if request.method == "POST":
        upload = request.FILES.get("csv_file")
        if not upload:
            errors.append("Selecciona un archivo CSV.")
        else:
            raw = upload.read()
            text = None
            for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
                try:
                    text = raw.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            if text is None:
                errors.append("No se pudo leer el archivo CSV. Revisa la codificación.")
            else:
                def normalize_header(value):
                    if value is None:
                        return ""
                    value = value.strip()
                    value = unicodedata.normalize("NFKD", value)
                    value = "".join(ch for ch in value if not unicodedata.combining(ch))
                    value = value.replace(" ", "_")
                    while "__" in value:
                        value = value.replace("__", "_")
                    return value.upper()

                header_map = {
                    "GD_SOCIEDAD": "gd_sociedad",
                    "GD_INTERNAL_CODE": "gd_internal_code",
                    "GD_DESCRIPCION": "gd_descripcion",
                    "GD_LOGO": "gd_logo",
                    "GD_CIF": "gd_cif",
                    "GD_FECHA_CONSTITUCION": "gd_fecha_constitucion",
                    "GD_DIRECCION": "gd_direccion",
                    "GD_CODIGO_POSTAL": "gd_codigo_postal",
                    "GD_CIUDAD": "gd_ciudad",
                    "GD_PROVINCIA": "gd_provincia",
                    "GD_COMUNIDAD_AUTONOMA": "gd_comunidad_autonoma",
                    "GD_PAIS": "gd_pais",
                    "GD_WEBSITE": "gd_website",
                    "GD_LINKEDIN": "gd_linkedin",
                    "GD_CEO": "gd_ceo",
                    "GD_EMAIL_CEO": "gd_email_ceo",
                    "GD_PHONE_CEO": "gd_phone_ceo",
                    "GD_PERSONA_CONTACTO_2": "gd_persona_contacto_2",
                    "GD_EMAIL_2": "gd_email_2",
                    "GD_PHONE_2": "gd_phone_2",
                    "GD_PERSONA_CONTACTO_3": "gd_persona_contacto_3",
                    "GD_EMAIL_3": "gd_email_3",
                    "GD_PHONE_3": "gd_phone_3",
                    "GD_OPI": "gd_opi",
                    "GD_ORGANO_ADMON": "gd_organo_admon",
                    "GD_FONDO": "gd_fondo",
                    "GD_FONDO_MIEMBRO_EQUIPO": "gd_fondo_miembro_equipo",
                    "CD_ESTADIO": "cd_estadio",
                    "CD_TECH_SECTOR": "cd_tech_sector",
                    "CD_TECH_SUBSECTOR": "cd_tech_subsector",
                    "CD_INDUSTRIAL_SECTOR": "cd_industrial_sector",
                    "CD_INDUSTRIAL_SUBSECTOR": "cd_industrial_subsector",
                    "SD_VALOR_DIFERENCIAL_TECNOLOGICO": "sd_valor_diferencial_tecnologico",
                    "SD_VALOR_DIFERENCIAL_MERCADO": "sd_valor_diferencial_mercado",
                    "SD_PROPUESTA_DE_VALOR": "sd_propuesta_de_valor",
                    "SD_BUSINESS_MODEL": "sd_business_model",
                    "SD_CLIENTES": "sd_clientes",
                    "SD_COMPETIDORES": "sd_competidores",
                    "MKT_TAM_DESCRIPCION": "mkt_tam_descripcion",
                    "MKT_TAM_VOLUME": "mkt_tam_volume",
                    "MKT_TAM_VALUE": "mkt_tam_value",
                    "MKT_TAM_CAGR": "mkt_tam_cagr",
                    "MKT_SAM_DESCRIPCION": "mkt_sam_descripcion",
                    "MKT_SAM_VOLUME": "mkt_sam_volume",
                    "MKT_SAM_VALUE": "mkt_sam_value",
                    "MKT_SAM_CAGR": "mkt_sam_cagr",
                    "MKT_SOM_DESCRIPCION": "mkt_som_descripcion",
                    "MKT_SOM_VOLUME": "mkt_som_volume",
                    "MKT_SOM_VALUE": "mkt_som_value",
                    "MKT_SOM_CAGR": "mkt_som_cagr",
                    "EXIT_VALUE": "exit_value",
                    "EXIT_DESCRIPCION": "exit_descripcion",
                    "EXIT_EMPRESAS_COMPARABLES": "exit_empresas_comparables",
                }

                sample = text[:4096]
                delimiter = ";"
                try:
                    dialect = csv.Sniffer().sniff(sample, delimiters=";,")
                    delimiter = dialect.delimiter
                except csv.Error:
                    delimiter = ";"

                reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

                def parse_decimal(value):
                    if value is None:
                        return None
                    value = value.strip()
                    if not value:
                        return None
                    if "," in value and "." in value:
                        value = value.replace(".", "").replace(",", ".")
                    elif "," in value and "." not in value:
                        value = value.replace(",", ".")
                    try:
                        return Decimal(value)
                    except InvalidOperation:
                        return None

                def parse_date(value):
                    if value is None:
                        return None
                    value = value.strip()
                    if not value:
                        return None
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                        try:
                            return datetime.datetime.strptime(value, fmt).date()
                        except ValueError:
                            continue
                    return None

                import datetime

                fondo_lookup = {
                    "beable innvierte science equity fund, fcre": "Beable Innvierte Science Equity Fund, FCRE",
                    "beable innvierte kets fund, f.c.r.": "Beable Innvierte Kets Fund, F.C.R.",
                }
                fondo_miembro_lookup = {
                    "david lopez garcia": "David López García",
                    "roberto ranera redondo": "Roberto Ranera Redondo",
                    "alberto diaz gonzalez": "Alberto Diaz González",
                    "almudena trigo redondo": "Almudena Trigo Redondo",
                }
                estadio_lookup = {
                    "pre-seed": "Pre-Seed",
                    "seed": "Seed",
                    "early stage": "Early Stage",
                    "venture capital": "Venture Capital",
                    "growth capital": "Growth Capital",
                    "expantion capital": "Expantion Capital",
                }
                tech_sector_lookup = {
                    "advanced materials": "Advanced Materials",
                    "nanotecnology": "Nanotecnology",
                    "micro & nanoelectronics": "Micro & Nanoelectronics",
                    "photonics": "Photonics",
                    "industrial biotechnology": "Industrial biotechnology",
                    "health tech/med tech": "Health tech/Med Tech",
                    "pharma (apis)": "Pharma (APIs)",
                    "advanced manufactoring and processing": "Advanced Manufactoring and Processing",
                    "algorithms (data mining, ia, itc...)": "Algorithms (Data Mining, IA, ITC...)",
                    "other": "Other",
                }

                for index, row in enumerate(reader, start=2):
                    data = {}
                    row_errors = []
                    for key, value in row.items():
                        if key is None:
                            continue
                        normalized = normalize_header(key)
                        field = header_map.get(normalized)
                        if not field:
                            continue
                        if field in {
                            "mkt_tam_volume",
                            "mkt_tam_value",
                            "mkt_tam_cagr",
                            "mkt_sam_volume",
                            "mkt_sam_value",
                            "mkt_sam_cagr",
                            "mkt_som_volume",
                            "mkt_som_value",
                            "mkt_som_cagr",
                            "exit_value",
                        }:
                            data[field] = parse_decimal(value)
                        elif field == "gd_fecha_constitucion":
                            data[field] = parse_date(value)
                        elif field == "gd_logo":
                            # No se soporta carga de imagenes por CSV.
                            continue
                        elif field == "gd_fondo":
                            raw_value = (value or "").strip()
                            if not raw_value:
                                data[field] = None
                            else:
                                normalized = raw_value.strip().lower()
                                canonical = fondo_lookup.get(normalized, raw_value)
                                fondo = Fondo.objects.filter(nombre__iexact=canonical).first()
                                if not fondo:
                                    row_errors.append(
                                        f"Fila {index}: GD_FONDO no coincide con ningún fondo válido."
                                    )
                                else:
                                    data[field] = fondo
                        elif field == "gd_fondo_miembro_equipo":
                            raw_value = (value or "").strip()
                            if not raw_value:
                                data[field] = None
                            else:
                                normalized = raw_value.strip().lower()
                                canonical = fondo_miembro_lookup.get(normalized, raw_value)
                                miembro = FondoMiembroEquipo.objects.filter(nombre__iexact=canonical).first()
                                if not miembro:
                                    row_errors.append(
                                        f"Fila {index}: GD_FONDO_MIEMBRO_EQUIPO no coincide con ningún miembro válido."
                                    )
                                else:
                                    data[field] = miembro
                        elif field == "cd_estadio":
                            raw_value = (value or "").strip()
                            if not raw_value:
                                data[field] = None
                            else:
                                normalized = raw_value.strip().lower()
                                canonical = estadio_lookup.get(normalized, raw_value)
                                estadio = Estadio.objects.filter(nombre__iexact=canonical).first()
                                if not estadio:
                                    row_errors.append(
                                        f"Fila {index}: CD_ESTADIO no coincide con ningún estadio válido."
                                    )
                                else:
                                    data[field] = estadio
                        elif field == "cd_tech_sector":
                            raw_value = (value or "").strip()
                            if not raw_value:
                                data[field] = None
                            else:
                                normalized = raw_value.strip().lower()
                                canonical = tech_sector_lookup.get(normalized, raw_value)
                                tech_sector = TechSector.objects.filter(nombre__iexact=canonical).first()
                                if not tech_sector:
                                    row_errors.append(
                                        f"Fila {index}: CD_TECH_SECTOR no coincide con ningún tech sector válido."
                                    )
                                else:
                                    data[field] = tech_sector
                        else:
                            data[field] = (value or "").strip()

                    if row_errors:
                        errors.extend(row_errors)
                        continue
                    if not data.get("gd_sociedad"):
                        errors.append(f"Fila {index}: GD_SOCIEDAD es obligatorio.")
                        continue
                    CompanyInvestment.objects.create(**data)
                    imported += 1

    return render(
        request,
        "core/company_import.html",
        {"active_page": "companies", "errors": errors, "imported": imported},
    )


@login_required(login_url=settings.LOGIN_URL)
def company_export_select(request):
    selected_ids = []
    if request.method == "POST":
        raw_ids = (request.POST.get("company_ids") or "").strip()
        if raw_ids:
            for value in raw_ids.split(","):
                value = value.strip()
                if value.isdigit():
                    selected_ids.append(int(value))

    companies_qs = _companies_for_user(request.user)
    companies = companies_qs.filter(pk__in=selected_ids) if selected_ids else companies_qs.none()

    export_fields = []
    for field in CompanyInvestment._meta.fields:
        if field.name == "id":
            continue
        export_fields.append(
            {
                "name": field.name,
                "label": str(field.verbose_name),
            }
        )

    return render(
        request,
        "core/company_export_select.html",
        {
            "active_page": "companies",
            "companies": companies,
            "selected_ids": ",".join(str(pk) for pk in selected_ids),
            "export_fields": export_fields,
        },
    )


@login_required(login_url=settings.LOGIN_URL)
def company_export_csv(request):
    if request.method != "POST":
        return HttpResponseRedirect(reverse("companies"))

    raw_ids = (request.POST.get("company_ids") or "").strip()
    selected_ids = []
    if raw_ids:
        for value in raw_ids.split(","):
            value = value.strip()
            if value.isdigit():
                selected_ids.append(int(value))

    selected_fields = request.POST.getlist("fields")
    if not selected_ids or not selected_fields:
        return HttpResponseRedirect(reverse("companies"))

    field_order = []
    for name in selected_fields:
        order_value = (request.POST.get(f"order_{name}") or "").strip()
        order = int(order_value) if order_value.isdigit() else 9999
        field_order.append((order, name))
    field_order.sort(key=lambda item: (item[0], item[1]))
    field_map = {
        field.name: field
        for field in CompanyInvestment._meta.fields
        if field.name != "id"
    }
    ordered_fields = [name for _, name in field_order if name in field_map]
    if not ordered_fields:
        return HttpResponseRedirect(reverse("companies"))

    companies = _companies_for_user(request.user).filter(pk__in=selected_ids)

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="companies_export.csv"'
    response.write("\ufeff")
    writer = csv.writer(response, delimiter=";")

    headers = [str(field_map[name].verbose_name) for name in ordered_fields]
    writer.writerow(headers)

    def format_value(obj, field):
        value = getattr(obj, field.name)
        if value is None:
            return ""
        if field.is_relation and hasattr(value, "nombre"):
            return value.nombre
        if field.is_relation:
            return str(value)
        if field.get_internal_type() in {"DateField", "DateTimeField"}:
            return value.isoformat()
        if field.get_internal_type() in {"ImageField", "FileField"}:
            return value.url if value else ""
        return value

    for company in companies:
        row = []
        for name in ordered_fields:
            field = field_map.get(name)
            if not field:
                row.append("")
                continue
            row.append(format_value(company, field))
        writer.writerow(row)

    return response


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def sectors(request):
    if request.method == "POST":
        form = SectorForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("sectors"))
    else:
        form = SectorForm()

    sectors = Sector.objects.order_by("nombre")
    return render(
        request,
        "core/sectors.html",
        {"sectors": sectors, "active_page": "sectors", "form": form},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def sector_delete(request, sector_id):
    sector = get_object_or_404(Sector, pk=sector_id)
    if request.method == "POST":
        sector.delete()
        return HttpResponseRedirect(reverse("sectors"))

    return render(
        request,
        "core/sector_confirm_delete.html",
        {"sector": sector, "active_page": "sectors"},
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def smtp_config(request):
    config, _ = SMTPConfig.objects.get_or_create(pk=1)
    success = None
    test_success = None
    test_error = None

    if request.method == "POST":
        action = request.POST.get("action", "save")

        if action == "test_email":
            recipient = request.POST.get("test_recipient", "").strip()
            if not recipient:
                test_error = "Introduce un email de destino para la prueba."
            elif not config.host:
                test_error = "Guarda primero la configuración SMTP antes de enviar un email de prueba."
            else:
                try:
                    from django.core.mail import EmailMessage
                    from django.core.mail.backends.smtp import EmailBackend

                    backend = EmailBackend(
                        host=config.host,
                        port=config.port,
                        username=config.username,
                        password=config.password,
                        use_tls=config.use_tls,
                        use_ssl=config.use_ssl,
                        timeout=10,
                        fail_silently=False,
                    )
                    msg = EmailMessage(
                        subject="Email de prueba – DataContaBL",
                        body=(
                            "Este es un email de prueba enviado desde DataContaBL "
                            "para verificar la configuración SMTP.\n\n"
                            f"Servidor: {config.host}:{config.port}\n"
                            f"Usuario: {config.username}"
                        ),
                        from_email=(
                            f"{config.from_name} <{config.from_email}>"
                            if config.from_name and config.from_email
                            else (config.from_email or config.username)
                        ),
                        to=[recipient],
                        connection=backend,
                    )
                    msg.send()
                    test_success = f"Email de prueba enviado correctamente a {recipient}."
                except Exception as exc:
                    test_error = f"Error al enviar: {exc}"
            form = SMTPConfigForm(instance=config)

        else:
            form = SMTPConfigForm(request.POST, instance=config)
            if form.is_valid():
                form.save()
                config.refresh_from_db()
                success = "Configuración SMTP guardada correctamente."
                form = SMTPConfigForm(instance=config)
    else:
        form = SMTPConfigForm(instance=config)

    return render(
        request,
        "core/smtp_config.html",
        {
            "form": form,
            "config": config,
            "active_page": "config",
            "success": success,
            "test_success": test_success,
            "test_error": test_error,
        },
    )


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(lambda u: u.is_staff, login_url="companies")
def reference_tables(request):
    table_messages = {}  # key → ("success"|"error", texto)

    if request.method == "POST":
        table_key = request.POST.get("table_key", "").strip()
        action = request.POST.get("action", "").strip()
        entry = _REF_TABLE_MAP.get(table_key)

        if entry:
            label, Model, has_orden = entry

            if action == "add":
                nombre = request.POST.get("nombre", "").strip()
                if not nombre:
                    table_messages[table_key] = ("error", "El nombre es obligatorio.")
                else:
                    try:
                        kwargs = {"nombre": nombre}
                        if has_orden:
                            try:
                                kwargs["orden"] = int(request.POST.get("orden") or 0)
                            except ValueError:
                                kwargs["orden"] = 0
                        Model.objects.create(**kwargs)
                        table_messages[table_key] = ("success", f"«{nombre}» añadido correctamente.")
                    except Exception as exc:
                        table_messages[table_key] = ("error", f"Error: {exc}")

            elif action == "edit":
                item_id = request.POST.get("item_id", "").strip()
                nombre = request.POST.get("nombre", "").strip()
                if not nombre:
                    table_messages[table_key] = ("error", "El nombre es obligatorio.")
                elif item_id:
                    try:
                        obj = get_object_or_404(Model, pk=item_id)
                        obj.nombre = nombre
                        if has_orden:
                            try:
                                obj.orden = int(request.POST.get("orden") or 0)
                            except ValueError:
                                obj.orden = 0
                        obj.save()
                        table_messages[table_key] = ("success", f"«{nombre}» actualizado correctamente.")
                    except Exception as exc:
                        table_messages[table_key] = ("error", f"Error: {exc}")

            elif action == "delete":
                item_id = request.POST.get("item_id", "").strip()
                if item_id:
                    try:
                        obj = get_object_or_404(Model, pk=item_id)
                        nombre = obj.nombre
                        obj.delete()
                        table_messages[table_key] = ("success", f"«{nombre}» eliminado.")
                    except Exception as exc:
                        table_messages[table_key] = ("error", f"Error: {exc}")

    tables = []
    for key, label, Model, has_orden in _REF_TABLES:
        msg = table_messages.get(key)
        tables.append({
            "key": key,
            "label": label,
            "has_orden": has_orden,
            "items": Model.objects.all(),
            "count": Model.objects.count(),
            "msg_type": msg[0] if msg else None,
            "msg_text": msg[1] if msg else None,
        })

    return render(
        request,
        "core/reference_tables.html",
        {"tables": tables, "active_page": "reference_tables"},
    )


# ── Recuperación de contraseña ────────────────────────────────────────────────

def password_reset_request(request):
    """Paso 1: el usuario introduce su email para recibir el enlace de reset."""
    smtp = _get_smtp()
    has_smtp = bool(smtp and smtp.host)
    error = None

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            error = "Introduce tu dirección de email."
        elif not has_smtp:
            error = "El sistema de email no está configurado. Contacta con el administrador."
        else:
            # Buscar usuarios activos con ese email (puede haber más de uno)
            matched = User.objects.filter(email__iexact=email, is_active=True)
            for user in matched:
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                reset_url = request.build_absolute_uri(
                    reverse("password_reset_confirm", args=[uid, token])
                )
                display = user.get_full_name() or user.username
                try:
                    from django.core.mail import EmailMessage
                    msg = EmailMessage(
                        subject="Recuperación de contraseña – DataContaBL",
                        body=(
                            f"Hola {display},\n\n"
                            f"Has solicitado restablecer tu contraseña en DataContaBL.\n\n"
                            f"Haz clic en el siguiente enlace para crear una nueva contraseña:\n"
                            f"{reset_url}\n\n"
                            f"Este enlace es válido durante 24 horas. Si no has solicitado "
                            f"este cambio, ignora este mensaje.\n\n"
                            f"El equipo de DataContaBL"
                        ),
                        from_email=_smtp_from_addr(smtp),
                        to=[user.email],
                        connection=_build_smtp_backend(smtp),
                    )
                    msg.send()
                except Exception:
                    pass  # No revelar errores para evitar enumeración de emails
            # Siempre redirigir a "done" (no revelar si el email existe o no)
            return HttpResponseRedirect(reverse("password_reset_done"))

    return render(request, "core/password_reset.html", {
        "has_smtp": has_smtp,
        "error": error,
    })


def password_reset_done(request):
    """Paso 2: confirmación de que el email fue enviado."""
    return render(request, "core/password_reset_done.html")


def password_reset_confirm(request, uidb64, token):
    """Paso 3: formulario para introducir la nueva contraseña."""
    error = None
    validlink = False
    user = None

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (User.DoesNotExist, ValueError, TypeError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        validlink = True
        if request.method == "POST":
            password1 = request.POST.get("new_password1", "")
            password2 = request.POST.get("new_password2", "")
            if not password1:
                error = "La contraseña no puede estar vacía."
            elif password1 != password2:
                error = "Las contraseñas no coinciden."
            elif len(password1) < 8:
                error = "La contraseña debe tener al menos 8 caracteres."
            else:
                user.set_password(password1)
                user.save()
                return HttpResponseRedirect(reverse("password_reset_complete"))

    return render(request, "core/password_reset_confirm.html", {
        "validlink": validlink,
        "error": error,
        "uidb64": uidb64,
        "token": token,
    })


def password_reset_complete(request):
    """Paso 4: contraseña cambiada con éxito."""
    return render(request, "core/password_reset_complete.html")
