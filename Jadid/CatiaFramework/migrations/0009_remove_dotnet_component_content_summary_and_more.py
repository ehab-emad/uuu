# Generated by Django 4.2.7 on 2024-01-26 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CatiaFramework', '0008_remove_dotnet_component_comment_tags_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dotnet_component',
            name='content_summary',
        ),
        migrations.AddField(
            model_name='dotnet_component',
            name='summary_section',
            field=models.CharField(blank=True, max_length=10000, null=True),
        ),
    ]
