# Generated by Django 3.2.18 on 2023-06-26 15:23

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataverses', '0002_alter_manifesttestparams_raw_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifesttestparams',
            name='raw_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/private_uploaded_data'), upload_to='mock-files/%Y/%m/%d/'),
        ),
    ]
