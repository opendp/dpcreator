# Generated by Django 3.2.18 on 2023-06-21 11:56

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataverses', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifesttestparams',
            name='raw_file',
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/code/server/test_setup/private_uploaded_data'), upload_to='mock-files/%Y/%m/%d/'),
        ),
    ]
