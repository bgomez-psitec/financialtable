from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_estadio_model_and_fk"),
    ]

    operations = [
        migrations.AddField(
            model_name="fondo",
            name="orden",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="fondomiembroequipo",
            name="orden",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="estadio",
            name="orden",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
