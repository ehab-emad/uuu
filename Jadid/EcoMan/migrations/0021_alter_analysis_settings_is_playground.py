# Generated by Django 4.2.10 on 2024-07-16 14:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EcoMan', '0020_analysis_settings_weight_units'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis_settings',
            name='is_playground',
            field=models.BooleanField(default=False, verbose_name='Job will be a comparison not visible as two column'),
        ),
    ]
