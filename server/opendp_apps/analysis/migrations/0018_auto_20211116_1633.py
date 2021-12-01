# Generated by Django 3.1.13 on 2021-11-16 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0017_auto_20211116_1457'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='auxiliaryfiledepositrecord',
            name='user_msg',
        ),
        migrations.AddField(
            model_name='auxiliaryfiledepositrecord',
            name='user_msg_html',
            field=models.TextField(blank=True, help_text='HTML version'),
        ),
        migrations.AddField(
            model_name='auxiliaryfiledepositrecord',
            name='user_msg_text',
            field=models.TextField(blank=True, help_text='text version'),
        ),
    ]
