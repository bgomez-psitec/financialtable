from django.db import migrations


VERTICAL_CLASIFICATIONS = [
    (1,  "Industrial Tech (Automotive)"),
    (2,  "Industrial Tech (Manufacturing)"),
    (3,  "Industrial Tech (Mining and Metals)"),
    (4,  "Industrial Tech (Oil and Gas)"),
    (5,  "Industrial Tech (Utilities)"),
    (6,  "Industrial Tech (Others)"),
    (7,  "Chem Tech (Chemicals)"),
    (8,  "Clean Tech (Energy and Utilities)"),
    (9,  "Clean Tech (Environment)"),
    (10, "Clean Tech (Others)"),
    (11, "Construc Tech"),
    (12, "Agro Tech (Agriculture and Food Processing)"),
    (13, "Food Tech"),
    (14, "Bio Tech (Biotechnology)"),
    (15, "Health Tech (Healthcare and Pharmaceuticals)"),
    (16, "Wealth Tech (IoT Care)"),
    (17, "Fin Tech (Banking and Financial Services)"),
    (18, "Prop Tech (Construction and Real Estate)"),
    (19, "Insur Tech (Insurance)"),
    (20, "Retail Tech (Retail, Wholesale & Consumer Goods)"),
    (21, "Logis Tech (Transportation and Logistics)"),
    (22, "Turist Tech (Tourism and Hospitality)"),
    (23, "Mar Tech (Media and Entertainment)"),
    (24, "Ed Tech (Education)"),
    (25, "ICT (Information Technology & Telecommunications)"),
    (26, "Other"),
]


def load_verticals(apps, schema_editor):
    VerticalClasification = apps.get_model("core", "VerticalClasification")
    for orden, nombre in VERTICAL_CLASIFICATIONS:
        VerticalClasification.objects.get_or_create(nombre=nombre, defaults={"orden": orden})


def unload_verticals(apps, schema_editor):
    VerticalClasification = apps.get_model("core", "VerticalClasification")
    nombres = [nombre for _, nombre in VERTICAL_CLASIFICATIONS]
    VerticalClasification.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_vertical_clasification_model_and_fk"),
    ]

    operations = [
        migrations.RunPython(load_verticals, reverse_code=unload_verticals),
    ]
