# Generated by Django 4.2 on 2023-08-08 21:45

from django.db import migrations, models
import django.db.models.deletion
import opendp_project.settings.base


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0004_alter_releaseinfo_dp_release_json_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisplan',
            name='release_info',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.releaseinfo'),
        ),
        migrations.AlterField(
            model_name='releaseinfo',
            name='dp_release_json_file',
            field=models.FileField(blank=True, null=True, storage=opendp_project.settings.base.RELEASE_FILE_STORAGE, upload_to='release-files/%Y/%m/%d/'),
        ),
        migrations.AlterField(
            model_name='releaseinfo',
            name='dp_release_pdf_file',
            field=models.FileField(blank=True, null=True, storage=opendp_project.settings.base.RELEASE_FILE_STORAGE, upload_to='release-files/%Y/%m/%d/'),
        ),
    ]
