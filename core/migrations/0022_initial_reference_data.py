from django.db import migrations


# ── Sectores (sin campo orden) ────────────────────────────────────────────────
SECTORES = [
    "Biotecnolog\u00eda",
    "Materiales Avanzados",
    "Energ\u00eda",
    "Medtech",
    "Agrotech",
    "Otro",
]

# ── Fondos ────────────────────────────────────────────────────────────────────
FONDOS = [
    (1, "Beable Innvierte Science Equity Fund, FCRE"),
    (2, "Beable Innvierte Kets Fund, F.C.R."),
]

# ── Miembros del equipo del fondo ─────────────────────────────────────────────
FONDO_MIEMBROS = [
    (1, "David L\u00f3pez Garc\u00eda"),
    (2, "Roberto Ranera Redondo"),
    (3, "Alberto Diaz Gonz\u00e1lez"),
    (4, "Almudena Trigo Redondo"),
]

# ── Estadios de inversión ─────────────────────────────────────────────────────
ESTADIOS = [
    (1, "Pre-Seed"),
    (2, "Seed"),
    (3, "Early Stage"),
    (4, "Venture Capital"),
    (5, "Growth Capital"),
    (6, "Expantion Capital"),
]

# ── Tech Sectors ──────────────────────────────────────────────────────────────
TECH_SECTORS = [
    (1,  "Advanced Materials"),
    (2,  "Nanotecnology"),
    (3,  "Micro & Nanoelectronics"),
    (4,  "Photonics"),
    (5,  "Industrial biotechnology"),
    (6,  "Health tech/Med Tech"),
    (7,  "Pharma (APIs)"),
    (8,  "Advanced Manufactoring and Processing"),
    (9,  "Algorithms (Data Mining, IA, ITC...)"),
    (10, "Other"),
]


def load_data(apps, schema_editor):
    Sector = apps.get_model("core", "Sector")
    for nombre in SECTORES:
        Sector.objects.get_or_create(nombre=nombre)

    Fondo = apps.get_model("core", "Fondo")
    for orden, nombre in FONDOS:
        Fondo.objects.get_or_create(nombre=nombre, defaults={"orden": orden})

    FondoMiembroEquipo = apps.get_model("core", "FondoMiembroEquipo")
    for orden, nombre in FONDO_MIEMBROS:
        FondoMiembroEquipo.objects.get_or_create(nombre=nombre, defaults={"orden": orden})

    Estadio = apps.get_model("core", "Estadio")
    for orden, nombre in ESTADIOS:
        Estadio.objects.get_or_create(nombre=nombre, defaults={"orden": orden})

    TechSector = apps.get_model("core", "TechSector")
    for orden, nombre in TECH_SECTORS:
        TechSector.objects.get_or_create(nombre=nombre, defaults={"orden": orden})


def unload_data(apps, schema_editor):
    Sector = apps.get_model("core", "Sector")
    Sector.objects.filter(nombre__in=SECTORES).delete()

    Fondo = apps.get_model("core", "Fondo")
    Fondo.objects.filter(nombre__in=[n for _, n in FONDOS]).delete()

    FondoMiembroEquipo = apps.get_model("core", "FondoMiembroEquipo")
    FondoMiembroEquipo.objects.filter(nombre__in=[n for _, n in FONDO_MIEMBROS]).delete()

    Estadio = apps.get_model("core", "Estadio")
    Estadio.objects.filter(nombre__in=[n for _, n in ESTADIOS]).delete()

    TechSector = apps.get_model("core", "TechSector")
    TechSector.objects.filter(nombre__in=[n for _, n in TECH_SECTORS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0021_smtpconfig"),
    ]

    operations = [
        migrations.RunPython(load_data, reverse_code=unload_data),
    ]
