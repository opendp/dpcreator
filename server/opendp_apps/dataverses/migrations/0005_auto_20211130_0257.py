# Generated by Django 3.1.13 on 2021-11-30 02:57

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataverses', '0004_remove_manifesttestparams_ddi_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifesttestparams',
            name='raw_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/code/server/test_setup/private_uploaded_data'), upload_to='mock-files/%Y/%m/%d/'),
        ),
    ]
