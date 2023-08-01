# Generated by Django 4.0 on 2023-07-28 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('analysis', '0002_initial'),
        ('user', '0001_initial'),
        ('dataset', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='analysisplan',
            name='analyst',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='user.opendpuser'),
        ),
        migrations.AddField(
            model_name='analysisplan',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataset.datasetinfo'),
        ),
        migrations.AddField(
            model_name='analysisplan',
            name='release_info',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.releaseinfo'),
        ),
    ]
