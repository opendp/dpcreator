# Generated by Django 3.1.2 on 2020-10-08 01:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_dataverseuser_installation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='GroupMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('membership_type', models.CharField(choices=[('AD', 'Admin'), ('ME', 'Member')], max_length=128)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.group')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.dataverseuser')),
            ],
        ),
    ]
