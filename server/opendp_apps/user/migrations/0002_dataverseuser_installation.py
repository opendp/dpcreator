# Generated by Django 3.1.2 on 2020-10-07 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataverseuser',
            name='installation',
            field=models.CharField(default='', max_length=128),
            preserve_default=False,
        ),
    ]
