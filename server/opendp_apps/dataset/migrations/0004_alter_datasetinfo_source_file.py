# Generated by Django 3.2.18 on 2023-06-26 15:23

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0003_alter_datasetinfo_source_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetinfo',
            name='source_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/private_uploaded_data'), upload_to='source-file/%Y/%m/%d/'),
        ),
    ]
