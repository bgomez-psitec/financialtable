# Migration rewritten to handle partial DB state:
# - core_techsubsector table may or may not exist
# - cd_tech_subsector_id column exists as varchar(120) (renamed by failed prior attempt)
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_vertical_clasification_data'),
    ]

    operations = [
        # 1. Create TechSubSector table (IF NOT EXISTS to be safe)
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS `core_techsubsector` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `nombre` varchar(255) NOT NULL,
                    `orden` int unsigned NOT NULL DEFAULT 0,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `core_techsubsector_nombre_uniq` (`nombre`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            reverse_sql="DROP TABLE IF EXISTS `core_techsubsector`;",
        ),
        # 2. Make the column nullable first (it was NOT NULL varchar), then clear it, then convert to bigint
        migrations.RunSQL(
            sql="ALTER TABLE `core_companyinvestment` MODIFY COLUMN `cd_tech_subsector_id` varchar(120) NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="UPDATE `core_companyinvestment` SET `cd_tech_subsector_id` = NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # 3. Change the column type from varchar(120) NULL to bigint NULL FK
        migrations.RunSQL(
            sql="ALTER TABLE `core_companyinvestment` MODIFY COLUMN `cd_tech_subsector_id` bigint NULL;",
            reverse_sql="ALTER TABLE `core_companyinvestment` MODIFY COLUMN `cd_tech_subsector_id` varchar(120) NOT NULL DEFAULT '';",
        ),
        # 4. Add FK constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE `core_companyinvestment`
                ADD CONSTRAINT `core_companyinvestment_cd_tech_subsector_fk`
                FOREIGN KEY (`cd_tech_subsector_id`)
                REFERENCES `core_techsubsector` (`id`)
                ON DELETE SET NULL;
            """,
            reverse_sql="ALTER TABLE `core_companyinvestment` DROP FOREIGN KEY `core_companyinvestment_cd_tech_subsector_fk`;",
        ),
        # 5. Tell Django's state machine what the field looks like now
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='TechSubSector',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('nombre', models.CharField(max_length=255, unique=True)),
                        ('orden', models.PositiveIntegerField(default=0)),
                    ],
                    options={
                        'verbose_name': 'Tech subsector',
                        'verbose_name_plural': 'Tech subsectors',
                        'ordering': ['orden', 'nombre'],
                    },
                ),
                migrations.AlterField(
                    model_name='companyinvestment',
                    name='cd_tech_subsector',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies', to='core.techsubsector', verbose_name='CD_TECH_SUBSECTOR'),
                ),
            ],
            database_operations=[],
        ),
    ]
