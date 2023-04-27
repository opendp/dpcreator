# Generated by Django 3.2.18 on 2023-04-27 17:47

from django.conf import settings
import django.core.files.storage
from django.db import migrations, models
import django.db.models.deletion
import opendp_apps.utils.extra_validators
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('dataset', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReleaseInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('epsilon_used', models.FloatField(validators=[opendp_apps.utils.extra_validators.validate_not_negative])),
                ('dp_release', models.JSONField()),
                ('dp_release_json_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/public_release_files'), upload_to='release-files/%Y/%m/%d/')),
                ('dp_release_pdf_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(location='/Users/ramanprasad/Documents/github-rp/dpcreator/server/test_setup/public_release_files'), upload_to='release-files/%Y/%m/%d/')),
                ('dataverse_deposit_info', models.JSONField(blank=True, help_text='Only applies to Dataverse files', null=True)),
                ('dv_json_deposit_complete', models.BooleanField(default=False, help_text='Only applies to Dataverse datasets')),
                ('dv_pdf_deposit_complete', models.BooleanField(default=False, help_text='Only applies to Dataverse datasets')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataset.datasetinfo')),
            ],
            options={
                'verbose_name': 'Release Information',
                'verbose_name_plural': 'Release Information',
                'ordering': ('dataset', '-created'),
            },
        ),
        migrations.CreateModel(
            name='ReleaseEmailRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('success', models.BooleanField(help_text='Did the mail go through?')),
                ('subject', models.CharField(max_length=255)),
                ('to_email', models.CharField(max_length=255)),
                ('from_email', models.CharField(max_length=255)),
                ('email_content', models.TextField(blank=True)),
                ('pdf_attached', models.BooleanField()),
                ('json_attached', models.BooleanField()),
                ('note', models.TextField(blank=True, help_text='Populated if mail not sent successfully')),
                ('release_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.releaseinfo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AuxiliaryFileDepositRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(blank=True, help_text='auto-filled on save', max_length=255)),
                ('deposit_success', models.BooleanField(default=False)),
                ('dv_auxiliary_type', models.CharField(choices=[('dpJson', 'dpJson'), ('dpPDF', 'dpPDF')], max_length=100)),
                ('dv_auxiliary_version', models.CharField(default='v1', help_text='e.g. "v1", "v2", etc', max_length=50)),
                ('http_status_code', models.IntegerField(default=-1, help_text='HTTP code')),
                ('http_resp_text', models.TextField(blank=True)),
                ('http_resp_json', models.JSONField(blank=True, null=True)),
                ('dv_err_msg', models.CharField(blank=True, max_length=255)),
                ('user_msg_text', models.TextField(blank=True, help_text='text version')),
                ('user_msg_html', models.TextField(blank=True, help_text='HTML version')),
                ('dv_download_url', models.URLField(blank=True)),
                ('release_info', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analysis.releaseinfo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AnalysisPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('is_complete', models.BooleanField(default=False)),
                ('user_step', models.CharField(choices=[('step_700', 'Step 7: Variables Confirmed'), ('step_800', 'Step 8: Statistics Created'), ('step_900', 'Step 9: Statistics Submitted'), ('step_1000', 'Step 10: Release Complete'), ('step_1100', 'Step 11: Dataverse Release Deposited'), ('step_1200', 'Step 12: Process Complete'), ('error_9500', 'Error 5: Release Creation Failed'), ('error_9600', 'Error 6: Release Deposit Failed')], max_length=128)),
                ('variable_info', models.JSONField(blank=True, null=True)),
                ('dp_statistics', models.JSONField(null=True)),
                ('analyst', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dataset.datasetinfo')),
                ('release_info', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='analysis.releaseinfo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
