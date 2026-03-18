from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Sector(models.Model):
    nombre = models.CharField(max_length=120, unique=True)

    class Meta:
        verbose_name = "Sector"
        verbose_name_plural = "Sectores"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Fondo(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Fondo"
        verbose_name_plural = "Fondos"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class FondoMiembroEquipo(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Fondo miembro equipo"
        verbose_name_plural = "Fondos miembros equipo"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class Estadio(models.Model):
    nombre = models.CharField(max_length=120, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Estadio"
        verbose_name_plural = "Estadios"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class TechSector(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Tech sector"
        verbose_name_plural = "Tech sectors"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class IndustrialSubSector(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Industrial subsector"
        verbose_name_plural = "Industrial subsectors"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class IndustrialSector(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Industrial sector"
        verbose_name_plural = "Industrial sectors"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class TechSubSector(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Tech subsector"
        verbose_name_plural = "Tech subsectors"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class VerticalClasification(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Vertical clasification"
        verbose_name_plural = "Vertical clasifications"
        ordering = ["orden", "nombre"]

    def __str__(self):
        return self.nombre


class CompanyInvestment(models.Model):
    gd_sociedad = models.CharField("GD_SOCIEDAD", max_length=255)
    gd_internal_code = models.CharField("GD_INTERNAL_CODE", max_length=120, blank=True)
    gd_descripcion = models.TextField("GD_DESCRIPCION", blank=True)
    gd_logo = models.ImageField("GD_LOGO", upload_to="company_logos/", blank=True, null=True)
    gd_cif = models.CharField("GD_CIF", max_length=40, blank=True)
    gd_fecha_constitucion = models.DateField("GD_FECHA_CONSTITUCION", blank=True, null=True)
    gd_direccion = models.CharField("GD_DIRECCION", max_length=255, blank=True)
    gd_codigo_postal = models.CharField("GD_CODIGO_POSTAL", max_length=20, blank=True)
    gd_ciudad = models.CharField("GD_CIUDAD", max_length=120, blank=True)
    gd_provincia = models.CharField("GD_PROVINCIA", max_length=120, blank=True)
    gd_comunidad_autonoma = models.CharField("GD_COMUNIDAD_AUTONOMA", max_length=120, blank=True)
    gd_pais = models.CharField("GD_PAIS", max_length=120, blank=True)
    gd_website = models.URLField("GD_Website", blank=True)
    gd_linkedin = models.URLField("GD_Linkedin", blank=True)
    gd_ceo = models.CharField("GD_CEO", max_length=120, blank=True)
    gd_email_ceo = models.EmailField("GD_Email_CEO", blank=True)
    gd_phone_ceo = models.CharField("GD_Phone_CEO", max_length=40, blank=True)
    gd_persona_contacto_2 = models.CharField("GD_PERSONA_CONTACTO_2", max_length=120, blank=True)
    gd_email_2 = models.EmailField("GD_EMAIL_2", blank=True)
    gd_phone_2 = models.CharField("GD_PHONE_2", max_length=40, blank=True)
    gd_persona_contacto_3 = models.CharField("GD_PERSONA_CONTACTO_3", max_length=120, blank=True)
    gd_email_3 = models.EmailField("GD_EMAIL_3", blank=True)
    gd_phone_3 = models.CharField("GD_PHONE_3", max_length=40, blank=True)
    gd_opi = models.CharField("GD_OPI", max_length=120, blank=True)
    gd_organo_admon = models.CharField("GD_ORGANO_ADMON", max_length=255, blank=True)
    gd_fondo = models.ForeignKey(
        Fondo,
        verbose_name="GD_FONDO",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    gd_fondo_miembro_equipo = models.ForeignKey(
        FondoMiembroEquipo,
        verbose_name="GD_FONDO_MIEMBRO_EQUIPO",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    cd_estadio = models.ForeignKey(
        Estadio,
        verbose_name="CD_ESTADIO",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    cd_tech_sector = models.ForeignKey(
        TechSector,
        verbose_name="CD_TECH_SECTOR",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    cd_vertical_clasification = models.ForeignKey(
        VerticalClasification,
        verbose_name="CD_VERTICAL_CLASIFICATION",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    cd_tech_subsector = models.ForeignKey(
        TechSubSector,
        verbose_name="CD_TECH_SUBSECTOR",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    cd_industrial_sector = models.ForeignKey(
        IndustrialSector,
        verbose_name="CD_INDUSTRIAL_SECTOR",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    cd_industrial_subsector = models.ForeignKey(
        IndustrialSubSector,
        verbose_name="CD_INDUSTRIAL_SUBSECTOR",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="companies",
    )
    sd_valor_diferencial_tecnologico = models.TextField("SD_VALOR_DIFERENCIAL_TECNOLOGICO", blank=True)
    sd_valor_diferencial_mercado = models.TextField("SD_VALOR_DIFERENCIAL_MERCADO", blank=True)
    sd_propuesta_de_valor = models.TextField("SD_PROPUESTA DE VALOR", blank=True)
    sd_business_model = models.TextField("SD_BUSINESS_MODEL", blank=True)
    sd_clientes = models.TextField("SD_CLIENTES", blank=True)
    sd_competidores = models.TextField("SD_COMPETIDORES", blank=True)
    mkt_tam_descripcion = models.TextField("MKT_TAM_Descripcion", blank=True)
    mkt_tam_volume = models.DecimalField("MKT_TAM_Volume", max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_tam_value = models.DecimalField("MKT_TAM_Value", max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_tam_cagr = models.DecimalField("MKT_TAM_CAGR", max_digits=6, decimal_places=2, blank=True, null=True)
    mkt_sam_descripcion = models.TextField("MKT_SAM_Descripcion", blank=True)
    mkt_sam_volume = models.DecimalField("MKT_SAM_Volume", max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_sam_value = models.DecimalField("MKT_SAM_Value", max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_sam_cagr = models.DecimalField("MKT_SAM_CAGR", max_digits=6, decimal_places=2, blank=True, null=True)
    mkt_som_descripcion = models.TextField("MKT_SOM_Descripcion", blank=True)
    mkt_som_volume = models.DecimalField("MKT_SOM_Volume", max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_som_value = models.DecimalField("MKT_SOM_Value", max_digits=18, decimal_places=2, blank=True, null=True)
    mkt_som_cagr = models.DecimalField("MKT_SOM_CAGR", max_digits=6, decimal_places=2, blank=True, null=True)
    exit_value = models.DecimalField("EXIT_VALUE", max_digits=18, decimal_places=2, blank=True, null=True)
    exit_descripcion = models.TextField("EXIT_DESCRIPCION", blank=True)
    exit_empresas_comparables = models.TextField("EXIT_EMPRESAS_COMPARABLES", blank=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["gd_sociedad"]

    def __str__(self):
        return self.gd_sociedad


class KPIEmpresa(models.Model):
    TRIMESTRE_CHOICES = [
        ("Q1", "Q1"),
        ("Q2", "Q2"),
        ("Q3", "Q3"),
        ("Q4", "Q4"),
    ]
    SN_CHOICES = [("S", "S"), ("N", "N")]
    TRL_MRL_CHOICES = [(i, str(i)) for i in range(1, 10)]

    # ── Identificación ──────────────────────────────────────────────────────
    sociedad = models.ForeignKey(
        CompanyInvestment,
        verbose_name="Sociedad",
        on_delete=models.CASCADE,
        related_name="kpis",
    )
    anio = models.PositiveIntegerField("Año")
    trimestre = models.CharField("Trimestre", max_length=2, choices=TRIMESTRE_CHOICES)

    # ── Datos generales del KPI ──────────────────────────────────────────────
    nombre = models.CharField("Nombre", max_length=255, blank=True)
    trl = models.PositiveSmallIntegerField(
        "TRL", null=True, blank=True, choices=TRL_MRL_CHOICES
    )
    mrl = models.PositiveSmallIntegerField(
        "MRL", null=True, blank=True, choices=TRL_MRL_CHOICES
    )
    estimated_breakeven_year = models.PositiveIntegerField(
        "Estimated Breakeven Year", null=True, blank=True
    )
    estimated_time_to_market = models.PositiveIntegerField(
        "Estimated Time to Market", null=True, blank=True
    )

    # ── Hitos (S/N) ─────────────────────────────────────────────────────────
    prueba_laboratorio_validada = models.CharField(
        "Prueba de laboratorio validada", max_length=1, choices=SN_CHOICES, blank=True
    )
    pilot_plant_terminada = models.CharField(
        "Pilot Plant terminada", max_length=1, choices=SN_CHOICES, blank=True
    )
    producto_pilot_plant_validado = models.CharField(
        "Producto de Pilot Plant / MVP validado por cliente",
        max_length=1, choices=SN_CHOICES, blank=True,
    )
    flagship_plant_terminada = models.CharField(
        "Flagship Plant terminada", max_length=1, choices=SN_CHOICES, blank=True
    )
    producto_flagship_validado = models.CharField(
        "Producto de Flagship validado por cliente",
        max_length=1, choices=SN_CHOICES, blank=True,
    )
    comercializacion = models.CharField(
        "Comercialización", max_length=1, choices=SN_CHOICES, blank=True
    )

    # ── Bus. Dev. ────────────────────────────────────────────────────────────
    nuevos_leads_clientes = models.PositiveIntegerField(
        "Nuevos Leads Clientes (contactados)", null=True, blank=True
    )
    qualified_clientes = models.PositiveIntegerField(
        "Qualified Clientes (interesados y estudiando los productos)", null=True, blank=True
    )
    ndas_clientes_firmados = models.PositiveIntegerField(
        "NDAs Clientes firmados", null=True, blank=True
    )
    loi_clientes_firmados = models.PositiveIntegerField(
        "LOI Clientes firmados (vigentes)", null=True, blank=True
    )
    presupuestos_clientes_enviados = models.PositiveIntegerField(
        "Presupuestos Clientes enviados pendiente de firma (< 3 meses)", null=True, blank=True
    )
    presupuestos_clientes_firmados = models.PositiveIntegerField(
        "Presupuestos Clientes firmados", null=True, blank=True
    )
    acuerdos_distribucion_firmados = models.PositiveIntegerField(
        "Acuerdos Distribución firmados", null=True, blank=True
    )
    acuerdos_colaboracion_clientes_firmados = models.PositiveIntegerField(
        "Acuerdos Colaboración Clientes firmados", null=True, blank=True
    )

    # ── Indicadores de rendimiento (%) ──────────────────────────────────────
    rendimiento_proceso = models.DecimalField(
        "Rendimiento del proceso (% real vs estimado)",
        max_digits=6, decimal_places=2, null=True, blank=True,
    )
    reproducibilidad_experimental = models.DecimalField(
        "Reproducibilidad experimental (% de variabilidad entre ensayos)",
        max_digits=6, decimal_places=2, null=True, blank=True,
    )
    coste_energetico = models.DecimalField(
        "Coste energético (% real vs estimado)",
        max_digits=6, decimal_places=2, null=True, blank=True,
    )
    coste_materias_primas = models.DecimalField(
        "Coste de materias primas (% real vs estimado)",
        max_digits=6, decimal_places=2, null=True, blank=True,
    )

    class Meta:
        verbose_name = "KPI Empresa"
        verbose_name_plural = "KPIs Empresas"
        unique_together = [("sociedad", "anio", "trimestre")]
        ordering = ["sociedad", "-anio", "trimestre"]

    def __str__(self):
        return f"{self.sociedad} — {self.anio} {self.trimestre}"


class SMTPConfig(models.Model):
    host = models.CharField("Servidor SMTP", max_length=255, default="smtp.gmail.com")
    port = models.PositiveIntegerField("Puerto", default=587)
    username = models.CharField("Usuario", max_length=255, blank=True)
    password = models.CharField("Contraseña", max_length=255, blank=True)
    from_email = models.EmailField("Email remitente", blank=True)
    from_name = models.CharField("Nombre remitente", max_length=255, blank=True)
    use_tls = models.BooleanField("Usar TLS", default=True)
    use_ssl = models.BooleanField("Usar SSL", default=False)
    updated_at = models.DateTimeField("Última actualización", auto_now=True)

    class Meta:
        verbose_name = "Configuración SMTP"
        verbose_name_plural = "Configuración SMTP"

    def __str__(self):
        return f"SMTP: {self.host}:{self.port}"


class UserCompanyInvestment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company_links",
    )
    company = models.ForeignKey(
        CompanyInvestment,
        on_delete=models.CASCADE,
        related_name="user_links",
    )

    class Meta:
        verbose_name = "Empresa asociada a usuario"
        verbose_name_plural = "Empresas asociadas a usuarios"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "company"],
                name="unique_user_company",
            ),
        ]

    def __str__(self):
        return f"{self.user} - {self.company}"


class UserProfile(models.Model):
    """Perfil extendido de usuario — actualmente gestiona el flag solo-lectura."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    is_readonly = models.BooleanField(
        "Solo lectura",
        default=False,
        help_text="Si está activo, el usuario puede ver datos pero no crear ni modificar.",
    )

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def _auto_create_user_profile(sender, instance, created, **kwargs):
    """Crea automáticamente un UserProfile cuando se crea un nuevo usuario."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
