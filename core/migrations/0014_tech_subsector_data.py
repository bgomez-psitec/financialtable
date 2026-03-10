from django.db import migrations


TECH_SUBSECTORS = [
    (1,  "Advanced Materials - Composites"),
    (2,  "Advanced Materials - Organic chemistry"),
    (3,  "Advanced Materials - Inorganic chemistry"),
    (4,  "Advanced Materials \u2013 Others"),
    (5,  "Nanotechnology - Nanostructured materials"),
    (6,  "Nanotechnology - Nanoparticles"),
    (7,  "Nanotechnology - Others"),
    (8,  "Microelectronics or Nanoelectronics - Integrated circuits"),
    (9,  "Microelectronics or Nanoelectronics - Discrete Transistors and diodes"),
    (10, "Microelectronics or Nanoelectronics - RF and microwave devices"),
    (11, "Microelectronics or Nanoelectronics \u2013 Others"),
    (12, "Photonics - Amplifiers"),
    (13, "Photonics - Bio photonics"),
    (14, "Photonics - Detection"),
    (15, "Photonics - Light sources"),
    (16, "Photonics - Modulation"),
    (17, "Photonics - Photonic integrated circuits"),
    (18, "Photonics - Photonic systems"),
    (19, "Photonics - Transmission media"),
    (20, "Photonics - Others"),
    (21, "Advanced Manufacturing and Processing - Additive manufacturing"),
    (22, "Advanced Manufacturing and Processing - Engineering designs"),
    (23, "Advanced Manufacturing and Processing - Machinery and equipment"),
    (24, "Advanced Manufacturing and Processing - Robotics"),
    (25, "Advanced Manufacturing and Processing - Others"),
    (26, "Advanced Manufacturing and Processing"),
    (27, "Industrial Biotechnology - Grey biotech (Environmental)"),
    (28, "Industrial Biotechnology - Red biotech (Pharma)"),
    (29, "Industrial Biotechnology - Blue biotech (Sea resources)"),
    (30, "Industrial Biotechnology - Green biotech (Agrotech)"),
    (31, "Industrial Biotechnology \u2013 Others"),
    (32, "Industrial Biotechnology - White biotech (Industrial Production)"),
    (33, "Industrial Biotechnology - Yellow biotech (Food)"),
    (34, "Pharmaceutical Ingredients"),
    (35, "Algorithms - Data Mining"),
    (36, "Algorithms - Artificial Intelligence"),
    (37, "Algorithms - ICT"),
    (38, "Other ICT"),
    (39, "Integration of technologies"),
    (40, "Other"),
]


def load_subsectors(apps, schema_editor):
    TechSubSector = apps.get_model("core", "TechSubSector")
    for orden, nombre in TECH_SUBSECTORS:
        TechSubSector.objects.get_or_create(nombre=nombre, defaults={"orden": orden})


def unload_subsectors(apps, schema_editor):
    TechSubSector = apps.get_model("core", "TechSubSector")
    nombres = [nombre for _, nombre in TECH_SUBSECTORS]
    TechSubSector.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_tech_subsector_model_and_fk"),
    ]

    operations = [
        migrations.RunPython(load_subsectors, reverse_code=unload_subsectors),
    ]
