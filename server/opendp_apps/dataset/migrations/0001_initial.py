# Generated by Django 3.2.18 on 2023-07-10 21:45

import django.core.files.storage
import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import opendp_apps.dataset.dataset_question_validators
import opendp_apps.utils.extra_validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataSetInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=128)),
                ('source', models.CharField(choices=[('upload', 'Upload'), ('dataverse', 'Dataverse')], max_length=128)),
                ('source_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/private_uploaded_data'), upload_to='source-file/%Y/%m/%d/')),
            ],
            options={
                'verbose_name': 'Dataset Information',
                'verbose_name_plural': 'Dataset Information',
                'ordering': ('name', '-created'),
            },
        ),
        migrations.CreateModel(
            name='DepositorSetupInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('is_complete', models.BooleanField(default=False, help_text='auto-populated on save')),
                ('user_step', models.CharField(choices=[('step_000', 'Step 0: Initialized'), ('step_100', 'Step 1: Uploaded'), ('step_200', 'Step 2: Validated'), ('step_300', 'Step 3: Profiling Processing'), ('step_400', 'Step 4: Profiling Complete'), ('step_500', 'Step 5: Variable Defaults Confirmed'), ('step_600', 'Step 6: Epsilon Set'), ('error_9100', 'Error 1: Validation Failed'), ('error_9200', 'Error 2: Dataverse Download Failed'), ('error_9300', 'Error 3: Profiling Failed'), ('error_9400', 'Error 4: Create Release Failed')], default='step_000', max_length=128)),
                ('dataset_questions', models.JSONField(blank=True, null=True, validators=[opendp_apps.dataset.dataset_question_validators.validate_dataset_questions])),
                ('epsilon_questions', models.JSONField(blank=True, null=True, validators=[opendp_apps.dataset.dataset_question_validators.validate_epsilon_questions])),
                ('data_profile', models.JSONField(blank=True, default=None, encoder=django.core.serializers.json.DjangoJSONEncoder, help_text='Unverified data profile', null=True)),
                ('variable_info', models.JSONField(blank=True, null=True)),
                ('default_epsilon', models.FloatField(blank=True, help_text='Default based on answers to epsilon_questions.', null=True, validators=[opendp_apps.utils.extra_validators.validate_epsilon_or_none])),
                ('epsilon', models.FloatField(blank=True, help_text='Used for OpenDP operations, starts as the "default_epsilon" value but may be overridden by the user.', null=True, validators=[opendp_apps.utils.extra_validators.validate_epsilon_or_none])),
                ('default_delta', models.FloatField(blank=True, default=0.0, help_text='Default based on answers to epsilon_questions.', null=True, validators=[opendp_apps.utils.extra_validators.validate_not_negative])),
                ('delta', models.FloatField(blank=True, default=0.0, help_text='Used for OpenDP operations, starts as the "default_delta" value but may be overridden by the user.', null=True, validators=[opendp_apps.utils.extra_validators.validate_not_negative])),
                ('confidence_level', models.FloatField(choices=[(0.9, '90% CL'), (0.95, '95% CL'), (0.99, '99% CL')], default=0.95, help_text='Used for OpenDP operations, starts as the "default_delta" value but may be overridden by the user.')),
                ('wizard_step', models.CharField(default='step_100', help_text='Used by the UI to track the wizard step', max_length=128)),
            ],
            options={
                'verbose_name': 'Depositor Setup Data',
                'verbose_name_plural': 'Depositor Setup Data',
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='DataverseFileInfo',
            fields=[
                ('datasetinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dataset.datasetinfo')),
                ('dataverse_file_id', models.IntegerField()),
                ('dataset_doi', models.CharField(max_length=255)),
                ('file_doi', models.CharField(blank=True, max_length=255)),
                ('dataset_schema_info', models.JSONField(blank=True, null=True)),
                ('file_schema_info', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Dataverse File Information',
                'verbose_name_plural': 'Dataverse File Information',
                'ordering': ('name', '-created'),
            },
            bases=('dataset.datasetinfo',),
        ),
        migrations.CreateModel(
            name='UploadFileInfo',
            fields=[
                ('datasetinfo_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='dataset.datasetinfo')),
            ],
            options={
                'verbose_name': 'Upload File Information',
                'verbose_name_plural': 'Upload File Information',
                'ordering': ('name', '-created'),
            },
            bases=('dataset.datasetinfo',),
        ),
    ]
