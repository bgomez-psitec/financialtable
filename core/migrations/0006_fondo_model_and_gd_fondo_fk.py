from django.db import migrations, models
import django.db.models.deletion


def create_fondos(apps, schema_editor):
    Fondo = apps.get_model("core", "Fondo")
    CompanyInvestment = apps.get_model("core", "CompanyInvestment")

    fondos = [
        "Beable Innvierte Science Equity Fund, FCRE",
        "Beable Innvierte Kets Fund, F.C.R.",
    ]

    fondo_map = {}
    for name in fondos:
        fondo, _ = Fondo.objects.get_or_create(nombre=name)
        fondo_map[name.lower()] = fondo

    for company in CompanyInvestment.objects.all():
        raw = (company.gd_fondo or "").strip()
        if not raw:
            continue
        fondo = fondo_map.get(raw.lower())
        if fondo:
            company.gd_fondo_ref = fondo
            company.save(update_fields=["gd_fondo_ref"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_companyinvestment_new_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="Fondo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "verbose_name": "Fondo",
                "verbose_name_plural": "Fondos",
                "ordering": ["nombre"],
            },
        ),
        migrations.AddField(
            model_name="companyinvestment",
            name="gd_fondo_ref",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="companies",
                to="core.fondo",
                verbose_name="GD_FONDO",
            ),
        ),
        migrations.RunPython(create_fondos, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="companyinvestment",
            name="gd_fondo",
        ),
        migrations.RenameField(
            model_name="companyinvestment",
            old_name="gd_fondo_ref",
            new_name="gd_fondo",
        ),
    ]
