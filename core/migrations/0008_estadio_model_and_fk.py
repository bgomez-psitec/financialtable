from django.db import migrations, models
import django.db.models.deletion


def create_estadios(apps, schema_editor):
    Estadio = apps.get_model("core", "Estadio")
    CompanyInvestment = apps.get_model("core", "CompanyInvestment")

    estadios = [
        "Pre-Seed",
        "Seed",
        "Early Stage",
        "Venture Capital",
        "Growth Capital",
        "Expantion Capital",
    ]

    estadio_map = {}
    for name in estadios:
        estadio, _ = Estadio.objects.get_or_create(nombre=name)
        estadio_map[name.lower()] = estadio

    for company in CompanyInvestment.objects.all():
        raw = (company.cd_estadio or "").strip()
        if not raw:
            continue
        estadio = estadio_map.get(raw.lower())
        if estadio:
            company.cd_estadio_ref = estadio
            company.save(update_fields=["cd_estadio_ref"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_fondo_miembro_equipo_model_and_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="Estadio",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120, unique=True)),
            ],
            options={
                "verbose_name": "Estadio",
                "verbose_name_plural": "Estadios",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="companyinvestment",
            name="cd_estadio_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companies",
                to="core.estadio",
                verbose_name="CD_ESTADIO",
            ),
        ),
        migrations.RunPython(create_estadios, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="companyinvestment",
            name="cd_estadio",
        ),
        migrations.RenameField(
            model_name="companyinvestment",
            old_name="cd_estadio_ref",
            new_name="cd_estadio",
        ),
    ]
