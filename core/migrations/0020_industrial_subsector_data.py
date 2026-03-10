from django.db import migrations


INDUSTRIAL_SUBSECTORS = [
    (1,  "Energy. Efficiency & Savings - Breakthrough Industrial processes"),
    (2,  "Energy. Efficiency & Savings - Smart buildings"),
    (3,  "Energy. Efficiency & Savings - Smart grid, SDC, HEV, EV"),
    (4,  "Energy. Efficiency & Savings - Smart lighting"),
    (5,  "Energy. Green Power Generation - Bioenergy"),
    (6,  "Energy. Green Power Generation - Energy. Green Power Generation - Marine energy"),
    (7,  "Energy. Green Power Generation - Geothermal energy"),
    (8,  "Energy. Green Power Generation - Hydrogen & low carbon energy"),
    (9,  "Energy. Green Power Generation - Hydropower"),
    (10, "Energy. Green Power Generation - Solar PV"),
    (11, "Energy. Green Power Generation - Solar-thermal energy"),
    (12, "Energy. Green Power Generation - Wind energy"),
    (13, "Energy. Storage Systems - Chemical storage"),
    (14, "Energy. Storage Systems - Electric storage"),
    (15, "Energy. Storage Systems - Electrochemical storage"),
    (16, "Energy. Storage Systems - Mechanical storage"),
    (17, "Energy. Storage Systems - Thermal storage"),
    (18, "Responsible Consumption. Circular Economy - Alternative Raw Materials"),
    (19, "Responsible Consumption. Circular Economy - Higher durability/recyclability products"),
    (20, "Responsible Consumption. Circular Economy - Waste Treatment"),
    (21, "Responsible Consumption. Next-generation materials - Bio-based Goods"),
    (22, "Responsible Consumption. Next-generation materials - Eco-friendly Products"),
    (23, "Responsible Consumption. Next-generation materials - Lighter & Resistant Composites"),
    (24, "Responsible Consumption. Next-generation materials - Lower-Cost Supplies"),
    (25, "Responsible Consumption. Reliable Packaging - Active packaging"),
    (26, "Responsible Consumption. Reliable Packaging - Embedded Sensor & Indicators"),
    (27, "Responsible Consumption. Reliable Packaging - Smart Passports & Tags."),
    (28, "Responsible Consumption. Reliable Packaging - Track & Trace"),
    (29, "Responsible Consumption. Sustainable Food - Ecological Aquiculture"),
    (30, "Responsible Consumption. Sustainable Food - Low Carbon Food"),
    (31, "Responsible Consumption. Sustainable Food - Smart and precision farming"),
    (32, "Responsible Consumption. Sustainable Food - Sustainable agriculture"),
    (33, "Sustainable & Quality Life. Food Quality - Food Safety Technologies"),
    (34, "Sustainable & Quality Life. Food Quality - Functional Foods"),
    (35, "Sustainable & Quality Life. Food Quality - Nutraceuticals"),
    (36, "Sustainable & Quality Life. MedTech - Biomaterials/Implants"),
    (37, "Sustainable & Quality Life. MedTech - Instrumentation/equipment"),
    (38, "Sustainable & Quality Life. MedTech - PoC Devices"),
    (39, "Sustainable & Quality Life. Translational Medicine - Bioprinting & Tissue Engineering"),
    (40, "Sustainable & Quality Life. Translational Medicine - HTS Platforms"),
    (41, "Sustainable & Quality Life. Translational Medicine - Omics Science"),
    (42, "Sustainable & Quality Life. Translational Medicine - Science Imaging Technologies"),
    (43, "Sustainable & Quality Life. Translational Medicine - Smart & Functional Biomaterials"),
    (44, "Sustainable & Quality Life. Well Being Promotion - Advanced Computing & Photonics"),
    (45, "Sustainable & Quality Life. Well Being Promotion - Human Centric Lighting"),
    (46, "Sustainable & Quality Life. Well Being Promotion - Personal Care"),
    (47, "Sustainable & Quality Life. Well Being Promotion - Resilient Infrastructures"),
    (48, "Sustainable & Quality Life. Well Being Promotion - Safety at Work"),
    (49, "The Future Earth. Environmental Clean-Up - Eutrophication control"),
    (50, "The Future Earth. Environmental Clean-Up - Greenhouse Gases Removal"),
    (51, "The Future Earth. Environmental Clean-Up - Hazardous Chemicals Eliminating"),
    (52, "The Future Earth. Environmental Clean-Up - Plastics & Microplastics Disposal"),
    (53, "The Future Earth. Protect Biodiversity & Ecosytems - Conserve Flora & Fauna"),
    (54, "The Future Earth. Protect Biodiversity & Ecosytems - Halting Deforestation"),
    (55, "The Future Earth. Protect Biodiversity & Ecosytems - Promote Animal Welfare"),
    (56, "The Future Earth. Protect Biodiversity & Ecosytems - Protect Natural Habitats"),
    (57, "The Future Earth. Sustainable use of water - Monitoring Technologies"),
    (58, "The Future Earth. Sustainable use of water - Potabilization & Desalinization"),
    (59, "The Future Earth. Sustainable use of water - Reducing Water Footprint"),
    (60, "The Future Earth. Sustainable use of water - Safeguard fresh water"),
    (61, "Others - Others"),
]


def load_subsectors(apps, schema_editor):
    IndustrialSubSector = apps.get_model("core", "IndustrialSubSector")
    for orden, nombre in INDUSTRIAL_SUBSECTORS:
        IndustrialSubSector.objects.get_or_create(nombre=nombre, defaults={"orden": orden})


def unload_subsectors(apps, schema_editor):
    IndustrialSubSector = apps.get_model("core", "IndustrialSubSector")
    nombres = [nombre for _, nombre in INDUSTRIAL_SUBSECTORS]
    IndustrialSubSector.objects.filter(nombre__in=nombres).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0019_industrial_subsector_model_and_fk"),
    ]

    operations = [
        migrations.RunPython(load_subsectors, reverse_code=unload_subsectors),
    ]
