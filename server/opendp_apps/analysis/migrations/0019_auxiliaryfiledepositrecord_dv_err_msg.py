# Generated by Django 3.1.13 on 2021-11-16 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0018_auto_20211116_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='auxiliaryfiledepositrecord',
            name='dv_err_msg',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
