# Generated by Django 3.0.5 on 2021-03-01 17:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digilab_logger', '0006_statuslog_user'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='statuslog',
            options={'ordering': ('-create_datetime',), 'verbose_name': 'System Log Entry', 'verbose_name_plural': 'System Log Entries'},
        ),
    ]
