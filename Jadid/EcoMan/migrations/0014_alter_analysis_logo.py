# Generated by Django 4.2.7 on 2023-12-15 08:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EcoMan', '0013_alter_analysis_comparison_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysis',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/', verbose_name='Part Image'),
        ),
    ]
