# Generated by Django 4.2.7 on 2024-01-29 14:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0018_remove_workflow_stage_actions_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow_stage',
            name='parent_stage',
            field=models.ForeignKey(blank=True, default=None, help_text='Parent Dependent Session', null=True, on_delete=django.db.models.deletion.CASCADE, to='CatiaFramework.workflow_stage', verbose_name='Parent Stage'),
        ),
    ]
