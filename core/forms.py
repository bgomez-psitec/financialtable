from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import (
    CompanyInvestment,
    Estadio,
    Fondo,
    FondoMiembroEquipo,
    IndustrialSector,
    IndustrialSubSector,
    SMTPConfig,
    Sector,
    TechSector,
    TechSubSector,
    UserCompanyInvestment,
    VerticalClasification,
)


class UserCreateForm(UserCreationForm):
    companies = forms.ModelMultipleChoiceField(
        label="Empresas asociadas",
        queryset=CompanyInvestment.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["companies"].queryset = CompanyInvestment.objects.order_by("gd_sociedad")

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            companies = self.cleaned_data.get("companies")
            if companies is not None:
                UserCompanyInvestment.objects.filter(user=user).delete()
                UserCompanyInvestment.objects.bulk_create(
                    [UserCompanyInvestment(user=user, company=company) for company in companies]
                )
        return user


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        required=False,
        widget=forms.PasswordInput,
    )
    companies = forms.ModelMultipleChoiceField(
        label="Empresas asociadas",
        queryset=CompanyInvestment.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "is_active", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["companies"].queryset = CompanyInvestment.objects.order_by("gd_sociedad")
        if self.instance and self.instance.pk:
            self.fields["companies"].initial = CompanyInvestment.objects.filter(
                user_links__user=self.instance
            ).values_list("pk", flat=True)

    def clean(self):
        cleaned = super().clean()
        password1 = cleaned.get("password1")
        password2 = cleaned.get("password2")
        if password1 or password2:
            if not password1 or not password2:
                raise forms.ValidationError("Completa ambos campos de contraseña.")
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get("password1")
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
            companies = self.cleaned_data.get("companies")
            if companies is not None:
                UserCompanyInvestment.objects.filter(user=user).delete()
                UserCompanyInvestment.objects.bulk_create(
                    [UserCompanyInvestment(user=user, company=company) for company in companies]
                )
        return user


class CompanyInvestmentForm(forms.ModelForm):
    class Meta:
        model = CompanyInvestment
        fields = [
            "gd_sociedad",
            "gd_internal_code",
            "gd_descripcion",
            "gd_logo",
            "gd_cif",
            "gd_fecha_constitucion",
            "gd_direccion",
            "gd_codigo_postal",
            "gd_ciudad",
            "gd_provincia",
            "gd_comunidad_autonoma",
            "gd_pais",
            "gd_website",
            "gd_linkedin",
            "gd_ceo",
            "gd_email_ceo",
            "gd_phone_ceo",
            "gd_persona_contacto_2",
            "gd_email_2",
            "gd_phone_2",
            "gd_persona_contacto_3",
            "gd_email_3",
            "gd_phone_3",
            "gd_opi",
            "gd_organo_admon",
            "gd_fondo",
            "gd_fondo_miembro_equipo",
            "cd_estadio",
            "cd_tech_sector",
            "cd_vertical_clasification",
            "cd_tech_subsector",
            "cd_industrial_sector",
            "cd_industrial_subsector",
            "sd_valor_diferencial_tecnologico",
            "sd_valor_diferencial_mercado",
            "sd_propuesta_de_valor",
            "sd_business_model",
            "sd_clientes",
            "sd_competidores",
            "mkt_tam_descripcion",
            "mkt_tam_volume",
            "mkt_tam_value",
            "mkt_tam_cagr",
            "mkt_sam_descripcion",
            "mkt_sam_volume",
            "mkt_sam_value",
            "mkt_sam_cagr",
            "mkt_som_descripcion",
            "mkt_som_volume",
            "mkt_som_value",
            "mkt_som_cagr",
            "exit_value",
            "exit_descripcion",
            "exit_empresas_comparables",
        ]
        widgets = {
            "gd_fecha_constitucion": forms.DateInput(attrs={"type": "date"}),
            "gd_descripcion": forms.Textarea(attrs={"rows": 3}),
            "sd_valor_diferencial_tecnologico": forms.Textarea(attrs={"rows": 3}),
            "sd_valor_diferencial_mercado": forms.Textarea(attrs={"rows": 3}),
            "sd_propuesta_de_valor": forms.Textarea(attrs={"rows": 3}),
            "sd_business_model": forms.Textarea(attrs={"rows": 3}),
            "sd_clientes": forms.Textarea(attrs={"rows": 3}),
            "sd_competidores": forms.Textarea(attrs={"rows": 3}),
            "mkt_tam_descripcion": forms.Textarea(attrs={"rows": 3}),
            "mkt_sam_descripcion": forms.Textarea(attrs={"rows": 3}),
            "mkt_som_descripcion": forms.Textarea(attrs={"rows": 3}),
            "exit_descripcion": forms.Textarea(attrs={"rows": 3}),
            "exit_empresas_comparables": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault("class", "form-control-file")
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-control")
        if "gd_fondo" in self.fields:
            self.fields["gd_fondo"].queryset = Fondo.objects.order_by("orden", "nombre")
        if "gd_fondo_miembro_equipo" in self.fields:
            self.fields["gd_fondo_miembro_equipo"].queryset = (
                FondoMiembroEquipo.objects.order_by("orden", "nombre")
            )
        if "cd_estadio" in self.fields:
            self.fields["cd_estadio"].queryset = Estadio.objects.order_by("orden", "nombre")
        if "cd_tech_sector" in self.fields:
            self.fields["cd_tech_sector"].queryset = TechSector.objects.order_by("orden", "nombre")
        if "cd_tech_subsector" in self.fields:
            self.fields["cd_tech_subsector"].queryset = TechSubSector.objects.order_by("orden", "nombre")
        if "cd_industrial_sector" in self.fields:
            self.fields["cd_industrial_sector"].queryset = IndustrialSector.objects.order_by("orden", "nombre")
        if "cd_industrial_subsector" in self.fields:
            self.fields["cd_industrial_subsector"].queryset = IndustrialSubSector.objects.order_by("orden", "nombre")
        if "cd_vertical_clasification" in self.fields:
            self.fields["cd_vertical_clasification"].queryset = VerticalClasification.objects.order_by("orden", "nombre")
        if "gd_fecha_constitucion" in self.fields:
            self.fields["gd_fecha_constitucion"].widget = forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            )
            self.fields["gd_fecha_constitucion"].input_formats = ["%Y-%m-%d"]


class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ["nombre"]


class SMTPConfigForm(forms.ModelForm):
    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(
            attrs={"autocomplete": "new-password"},
            render_value=True,
        ),
        help_text="Deja en blanco para conservar la contraseña guardada.",
    )

    class Meta:
        model = SMTPConfig
        fields = ["host", "port", "username", "password", "from_email", "from_name", "use_tls", "use_ssl"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.PasswordInput)):
                field.widget.attrs.setdefault("class", "form-control")

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("use_tls") and cleaned.get("use_ssl"):
            raise forms.ValidationError("No puedes activar TLS y SSL al mismo tiempo.")
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        new_password = self.cleaned_data.get("password", "")
        if not new_password and self.instance.pk:
            try:
                instance.password = SMTPConfig.objects.get(pk=self.instance.pk).password
            except SMTPConfig.DoesNotExist:
                pass
        else:
            instance.password = new_password
        if commit:
            instance.save()
        return instance
