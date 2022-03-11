# Generated by Django 3.1.13 on 2022-03-11 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_opendpuser_handoff_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='opendpuser',
            name='handoff_id',
            field=models.UUIDField(default=None, help_text='Temporary storage of a DataverseHandoff.object_id when arriving from Dataverse.', null=True),
        ),
    ]