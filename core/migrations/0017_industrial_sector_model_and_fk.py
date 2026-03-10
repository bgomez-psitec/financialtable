import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_rename_cd_environmental_to_industrial_subsector'),
    ]

    operations = [
        # 1. Create IndustrialSector table
        migrations.RunSQL(
            sql="""
                CREATE TABLE IF NOT EXISTS `core_industrialsector` (
                    `id` bigint NOT NULL AUTO_INCREMENT,
                    `nombre` varchar(255) NOT NULL,
                    `orden` int unsigned NOT NULL DEFAULT 0,
                    PRIMARY KEY (`id`),
                    UNIQUE KEY `core_industrialsector_nombre_uniq` (`nombre`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """,
            reverse_sql="DROP TABLE IF EXISTS `core_industrialsector`;",
        ),
        # 2. Make varchar column nullable, clear it, convert to bigint FK
        migrations.RunSQL(
            sql="ALTER TABLE `core_companyinvestment` MODIFY COLUMN `cd_industrial_sector` varchar(120) NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="UPDATE `core_companyinvestment` SET `cd_industrial_sector` = NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql="ALTER TABLE `core_companyinvestment` CHANGE COLUMN `cd_industrial_sector` `cd_industrial_sector_id` bigint NULL;",
            reverse_sql="ALTER TABLE `core_companyinvestment` CHANGE COLUMN `cd_industrial_sector_id` `cd_industrial_sector` varchar(120) NOT NULL DEFAULT '';",
        ),
        # 3. Add FK constraint
        migrations.RunSQL(
            sql="""
                ALTER TABLE `core_companyinvestment`
                ADD CONSTRAINT `core_companyinvestment_cd_industrial_sector_fk`
                FOREIGN KEY (`cd_industrial_sector_id`)
                REFERENCES `core_industrialsector` (`id`)
                ON DELETE SET NULL;
            """,
            reverse_sql="ALTER TABLE `core_companyinvestment` DROP FOREIGN KEY `core_companyinvestment_cd_industrial_sector_fk`;",
        ),
        # 4. Sync Django state
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='IndustrialSector',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('nombre', models.CharField(max_length=255, unique=True)),
                        ('orden', models.PositiveIntegerField(default=0)),
                    ],
                    options={
                        'verbose_name': 'Industrial sector',
                        'verbose_name_plural': 'Industrial sectors',
                        'ordering': ['orden', 'nombre'],
                    },
                ),
                migrations.AlterField(
                    model_name='companyinvestment',
                    name='cd_industrial_sector',
                    field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='companies', to='core.industrialsector', verbose_name='CD_INDUSTRIAL_SECTOR'),
                ),
            ],
            database_operations=[],
        ),
    ]
