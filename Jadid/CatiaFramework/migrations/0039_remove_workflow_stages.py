# Generated by Django 4.2.7 on 2024-01-31 11:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0038_workflow_object_is_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='workflow',
            name='stages',
        ),
    ]
