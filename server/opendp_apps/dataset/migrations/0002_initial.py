# Generated by Django 3.2.18 on 2023-06-26 12:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('dataverses', '0001_initial'),
        ('dataset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositorsetupinfo',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='datasetinfo',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='datasetinfo',
            name='depositor_setup_info',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ds_info', to='dataset.depositorsetupinfo'),
        ),
        migrations.AddField(
            model_name='datasetinfo',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_dataset.datasetinfo_set+', to='contenttypes.contenttype'),
        ),
        migrations.AddField(
            model_name='dataversefileinfo',
            name='dv_installation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dataverses.registereddataverse'),
        ),
        migrations.AddConstraint(
            model_name='dataversefileinfo',
            constraint=models.UniqueConstraint(fields=('dv_installation', 'dataverse_file_id'), name='unique Dataverse file'),
        ),
    ]
