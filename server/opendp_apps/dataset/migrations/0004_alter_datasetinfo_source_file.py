# Generated by Django 4.0 on 2023-07-17 16:54

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0003_alter_datasetinfo_polymorphic_ctype_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datasetinfo',
            name='source_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/private_uploaded_data'), upload_to='source-file/%Y/%m/%d/'),
        ),
    ]
