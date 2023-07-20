# Generated by Django 4.0 on 2023-07-20 20:45

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('dataverses', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenDPUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('handoff_id', models.UUIDField(default=None, help_text='Temporary storage of a DataverseHandoff.object_id when arriving from Dataverse.', null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'OpenDP User',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
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
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.opendpuser')),
            ],
        ),
        migrations.CreateModel(
            name='DataverseUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('persistent_id', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=255)),
                ('first_name', models.CharField(blank=True, max_length=255)),
                ('last_name', models.CharField(blank=True, max_length=255)),
                ('dv_general_token', models.CharField(blank=True, max_length=255)),
                ('dv_installation', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='dataverses.registereddataverse')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.opendpuser')),
            ],
            options={
                'verbose_name': 'Dataverse User',
                'unique_together': {('user', 'dv_installation')},
            },
        ),
    ]
