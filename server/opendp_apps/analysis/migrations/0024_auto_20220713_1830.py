# Generated by Django 3.1.13 on 2022-07-13 18:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0007_auto_20211130_0257'),
        ('analysis', '0023_releaseemailrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='analysisplan',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataset.datasetinfo'),
        ),
        migrations.AlterField(
            model_name='releaseinfo',
            name='dataset',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataset.datasetinfo'),
        ),
    ]