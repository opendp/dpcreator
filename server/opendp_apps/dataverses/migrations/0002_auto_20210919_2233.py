# Generated by Django 3.1.12 on 2021-09-19 22:33

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
            field=models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/user_uploaded_data'), upload_to='mock-files/%Y/%m/%d/'),
        ),
    ]
