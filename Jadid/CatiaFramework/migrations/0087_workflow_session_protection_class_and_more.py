# Generated by Django 4.2.10 on 2024-06-05 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0086_workflow_modified'),
    ]

    operations = [
        migrations.AddField(
            model_name='workflow_session',
            name='protection_class',
            field=models.CharField(choices=[('PUBLIC', 'Public'), ('INTERNAL', 'Internal'), ('CONFIDENTIAL', 'Confidential'), ('STRICTLY_CONFIDENTIAL', 'Strictly Confidential')], default='CONFIDENTIAL', max_length=100, verbose_name='Analysis protection class'),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='modified',
            field=models.BooleanField(default=False, verbose_name='Status flag indicating the need to update the static structure.'),
        ),
    ]
