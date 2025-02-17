# Generated by Django 4.2.7 on 2024-02-05 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0045_alter_workflow_action_required_actions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='status',
            field=models.CharField(choices=[('IN_PROGRESS', 'In Progress'), ('DONE', 'Done'), ('FAILED', 'Failed'), ('UNDEFINED', 'Undefined'), ('UNDEFINED', 'Undefined')], default='UNDEFINED', max_length=50),
        ),
        migrations.AlterField(
            model_name='workflow_action',
            name='gif',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/', verbose_name='Animated Thumbnail'),
        ),
        migrations.AlterField(
            model_name='workflow_action',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/', verbose_name='Thumbnail'),
        ),
        migrations.AlterField(
            model_name='workflow_object',
            name='required_objects',
            field=models.ManyToManyField(blank=True, default=None, to='CatiaFramework.workflow_object', verbose_name='Required Objects'),
        ),
        migrations.AlterField(
            model_name='workflow_stage',
            name='gif',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/', verbose_name='Animated Thumbnail'),
        ),
        migrations.AlterField(
            model_name='workflow_stage',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='uploads/', verbose_name='Thumbnail'),
        ),
    ]
