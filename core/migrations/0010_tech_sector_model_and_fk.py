from django.db import migrations, models
import django.db.models.deletion


def create_tech_sectors(apps, schema_editor):
    TechSector = apps.get_model("core", "TechSector")
    CompanyInvestment = apps.get_model("core", "CompanyInvestment")

    tech_sectors = [
        ("Advanced Materials", 1),
        ("Nanotecnology", 2),
        ("Micro & Nanoelectronics", 3),
        ("Photonics", 4),
        ("Industrial biotechnology", 5),
        ("Health tech/Med Tech", 6),
        ("Pharma (APIs)", 7),
        ("Advanced Manufactoring and Processing", 8),
        ("Algorithms (Data Mining, IA, ITC...)", 9),
        ("Other", 10),
    ]

    sector_map = {}
    for name, orden in tech_sectors:
        sector, _ = TechSector.objects.get_or_create(nombre=name, defaults={"orden": orden})
        if sector.orden != orden:
            sector.orden = orden
            sector.save(update_fields=["orden"])
        sector_map[name.lower()] = sector

    for company in CompanyInvestment.objects.all():
        raw = (company.cd_tech_sector or "").strip()
        if not raw:
            continue
        sector = sector_map.get(raw.lower())
        if sector:
            company.cd_tech_sector_ref = sector
            company.save(update_fields=["cd_tech_sector_ref"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_add_orden_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="TechSector",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=255, unique=True)),
                ("orden", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Tech sector",
                "verbose_name_plural": "Tech sectors",
                "ordering": ["orden", "nombre"],
            },
        ),
        migrations.AddField(
            model_name="companyinvestment",
            name="cd_tech_sector_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companies",
                to="core.techsector",
                verbose_name="CD_TECH_SECTOR",
            ),
        ),
        migrations.RunPython(create_tech_sectors, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="companyinvestment",
            name="cd_tech_sector",
        ),
        migrations.RenameField(
            model_name="companyinvestment",
            old_name="cd_tech_sector_ref",
            new_name="cd_tech_sector",
        ),
    ]
