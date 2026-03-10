from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_tech_subsector_data'),
    ]

    operations = [
        migrations.RenameField(
            model_name='companyinvestment',
            old_name='cd_industrial_clasification',
            new_name='cd_industrial_sector',
        ),
    ]
