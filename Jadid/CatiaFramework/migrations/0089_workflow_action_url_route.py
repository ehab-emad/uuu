# Generated by Django 4.2.10 on 2024-07-16 06:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0088_remove_workflow_action_automatic_trigger_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow_action',
            name='url_route',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
