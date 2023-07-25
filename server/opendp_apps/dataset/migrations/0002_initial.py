# Generated by Django 4.0 on 2023-07-24 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dataset', '0001_initial'),
        ('dataverses', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='depositorsetupinfo',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.opendpuser'),
        ),
        migrations.AddField(
            model_name='datasetinfo',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.opendpuser'),
        ),
        migrations.AddField(
            model_name='datasetinfo',
            name='depositor_setup_info',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ds_info', to='dataset.depositorsetupinfo'),
        ),
        migrations.AddField(
            model_name='datasetinfo',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_%(app_label)s.%(class)s_set+', to='contenttypes.contenttype'),
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
