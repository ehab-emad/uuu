# Generated by Django 4.2.7 on 2024-02-12 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0052_remove_workflow_object_actions'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow_object',
            name='is_interactive',
            field=models.BooleanField(default=False, verbose_name='Object is activated'),
        ),
        migrations.AlterField(
            model_name='workflow_object',
            name='is_active',
            field=models.BooleanField(default=False, verbose_name='Object is activated'),
        ),
    ]
