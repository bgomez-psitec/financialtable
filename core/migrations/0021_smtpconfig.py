from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_industrial_subsector_data"),
    ]

    operations = [
        migrations.CreateModel(
            name="SMTPConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("host", models.CharField(default="smtp.gmail.com", max_length=255, verbose_name="Servidor SMTP")),
                ("port", models.PositiveIntegerField(default=587, verbose_name="Puerto")),
                ("username", models.CharField(blank=True, max_length=255, verbose_name="Usuario")),
                ("password", models.CharField(blank=True, max_length=255, verbose_name="Contraseña")),
                ("from_email", models.EmailField(blank=True, max_length=254, verbose_name="Email remitente")),
                ("from_name", models.CharField(blank=True, max_length=255, verbose_name="Nombre remitente")),
                ("use_tls", models.BooleanField(default=True, verbose_name="Usar TLS")),
                ("use_ssl", models.BooleanField(default=False, verbose_name="Usar SSL")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Última actualización")),
            ],
            options={
                "verbose_name": "Configuración SMTP",
                "verbose_name_plural": "Configuración SMTP",
            },
        ),
    ]
