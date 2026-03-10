from django.db import migrations, models
import django.db.models.deletion


def create_fondo_miembros(apps, schema_editor):
    FondoMiembroEquipo = apps.get_model("core", "FondoMiembroEquipo")
    CompanyInvestment = apps.get_model("core", "CompanyInvestment")

    miembros = [
        "David López García",
        "Roberto Ranera Redondo",
        "Alberto Diaz González",
        "Almudena Trigo Redondo",
    ]

    miembro_map = {}
    for name in miembros:
        miembro, _ = FondoMiembroEquipo.objects.get_or_create(nombre=name)
        miembro_map[name.lower()] = miembro

    for company in CompanyInvestment.objects.all():
        raw = (company.gd_fondo_miembro_equipo or "").strip()
        if not raw:
            continue
        miembro = miembro_map.get(raw.lower())
        if miembro:
            company.gd_fondo_miembro_equipo_ref = miembro
            company.save(update_fields=["gd_fondo_miembro_equipo_ref"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_fondo_model_and_gd_fondo_fk"),
    ]

    operations = [
        migrations.CreateModel(
            name="FondoMiembroEquipo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Fondo miembro equipo",
                "verbose_name_plural": "Fondos miembros equipo",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="companyinvestment",
            name="gd_fondo_miembro_equipo_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companies",
                to="core.fondomiembroequipo",
                verbose_name="GD_FONDO_MIEMBRO_EQUIPO",
            ),
        ),
        migrations.RunPython(create_fondo_miembros, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="companyinvestment",
            name="gd_fondo_miembro_equipo",
        ),
        migrations.RenameField(
            model_name="companyinvestment",
            old_name="gd_fondo_miembro_equipo_ref",
            new_name="gd_fondo_miembro_equipo",
        ),
    ]
