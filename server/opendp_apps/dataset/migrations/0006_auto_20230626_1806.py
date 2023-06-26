# Generated by Django 3.2.18 on 2023-06-26 18:06

import django.core.files.storage
import django.core.serializers.json
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0005_alter_datasetinfo_source_file'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='depositorsetupinfo',
            name='unverified_data_profile',
        ),
        migrations.AddField(
            model_name='depositorsetupinfo',
            name='data_profile',
            field=models.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Unverified data profile', null=True),
        ),
        migrations.AlterField(
            model_name='datasetinfo',
            name='source_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/private_uploaded_data'), upload_to='source-file/%Y/%m/%d/'),
        ),
    ]
