# Generated by Django 3.1.12 on 2021-09-13 22:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0010_auto_20210913_2233'),
        ('dataset', '0003_datasetinfo_profile_variables'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataversefileinfo',
            name='depositor_setup_info',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='analysis.depositorsetupinfo'),
        ),
        migrations.AlterField(
            model_name='uploadfileinfo',
            name='depositor_setup_info',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='analysis.depositorsetupinfo'),
        ),
    ]
