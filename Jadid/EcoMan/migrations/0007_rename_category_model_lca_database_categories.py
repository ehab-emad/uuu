# Generated by Django 4.2.7 on 2023-11-27 14:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EcoMan', '0006_alter_lca_database_accessibility'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lca_database',
            old_name='category_model',
            new_name='categories',
        ),
    ]
