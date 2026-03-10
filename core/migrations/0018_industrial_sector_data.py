from django.db import migrations


INDUSTRIAL_SECTORS = [
    (1,  "Energy. Efficiency & Savings"),
    (2,  "Energy. Green Power Generation"),
    (3,  "Energy. Storage Systems"),
    (4,  "Responsible Consumption. Circular Economy"),
    (5,  "Responsible Consumption. Next-generation materials"),
    (6,  "Responsible Consumption. Reliable Packaging"),
    (7,  "Responsible Consumption. Sustainable Food"),
    (8,  "Sustainable & Quality Life. Food Quality"),
    (9,  "Sustainable & Quality Life. MedTech"),
    (10, "Sustainable & Quality Life. Translational Medicine"),
    (11, "Sustainable & Quality Life. Well Being Promotion"),
    (12, "The Future Earth. Environmental Clean-Up"),
    (13, "The Future Earth. Protect Biodiversity & Ecosytems"),
    (14, "The Future Earth. Sustainable use of water"),
    (15, "Others - Others"),
]


def load_sectors(apps, schema_editor):
    IndustrialSector = apps.get_model("core", "IndustrialSector")
    for orden, nombre in INDUSTRIAL_SECTORS:
        IndustrialSector.objects.get_or_create(nombre=nombre, defaults={"orden": orden})


def unload_sectors(apps, schema_editor):
    IndustrialSector = apps.get_model("core", "IndustrialSector")
    nombres = [nombre for _, nombre in INDUSTRIAL_SECTORS]
    IndustrialSector.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_industrial_sector_model_and_fk"),
    ]

    operations = [
        migrations.RunPython(load_sectors, reverse_code=unload_sectors),
    ]
