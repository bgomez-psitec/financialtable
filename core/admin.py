from django.contrib import admin

from .models import CompanyInvestment, Estadio, Fondo, FondoMiembroEquipo, IndustrialSector, IndustrialSubSector, SMTPConfig, Sector, TechSector, TechSubSector, VerticalClasification


@admin.register(CompanyInvestment)
class CompanyInvestmentAdmin(admin.ModelAdmin):
    list_display = (
        "gd_sociedad",
        "gd_internal_code",
        "gd_cif",
        "gd_pais",
        "cd_estadio",
        "gd_ceo",
    )
    search_fields = ("gd_sociedad", "gd_internal_code", "gd_cif", "gd_pais", "gd_ceo")
    list_filter = ("gd_pais", "cd_estadio", "cd_tech_sector")


@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Fondo)
class FondoAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(FondoMiembroEquipo)
class FondoMiembroEquipoAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(Estadio)
class EstadioAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(TechSector)
class TechSectorAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(IndustrialSector)
class IndustrialSectorAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(IndustrialSubSector)
class IndustrialSubSectorAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(TechSubSector)
class TechSubSectorAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(VerticalClasification)
class VerticalClasificationAdmin(admin.ModelAdmin):
    list_display = ("orden", "nombre")
    search_fields = ("nombre",)


@admin.register(SMTPConfig)
class SMTPConfigAdmin(admin.ModelAdmin):
    list_display = ("host", "port", "username", "from_email", "use_tls", "use_ssl", "updated_at")
    readonly_fields = ("updated_at",)
