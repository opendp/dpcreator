# Generated by Django 4.0 on 2023-07-24 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('dataset', '0001_initial'),
        ('analysis', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='releaseinfo',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataset.datasetinfo'),
        ),
        migrations.AddField(
            model_name='releaseemailrecord',
            name='release_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.releaseinfo'),
        ),
        migrations.AddField(
            model_name='auxiliaryfiledepositrecord',
            name='release_info',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.releaseinfo'),
        ),
    ]
