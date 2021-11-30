# Generated by Django 3.1.13 on 2021-11-17 22:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0019_auxiliaryfiledepositrecord_dv_err_msg'),
    ]

    operations = [
        migrations.AddField(
            model_name='releaseinfo',
            name='dataverse_deposit_info',
            field=models.JSONField(blank=True, help_text='Only applies to Dataverse files', null=True),
        ),
    ]