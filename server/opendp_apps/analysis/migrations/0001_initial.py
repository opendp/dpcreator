# Generated by Django 3.1.12 on 2021-07-28 18:28

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisPlan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('name', models.CharField(max_length=255)),
                ('is_complete', models.BooleanField(default=False)),
                ('user_step', models.CharField(choices=[('step_500', 'Step 5: Variables Confirmed'), ('step_600', 'Step 6: Statistics Created'), ('step_700', 'Step 7: Statistics Submitted'), ('step_800', 'Step 8: Release Complete'), ('step_900', 'Step 9: Dataverse Release Deposited'), ('step_1000', 'Step 10: Process Complete'), ('error_9500', 'Error 5: Release Creation Failed'), ('error_9600', 'Error 6: Release Deposit Failed')], max_length=128)),
                ('variable_ranges', models.JSONField(null=True)),
                ('variable_categories', models.JSONField(null=True)),
                ('custom_variables', models.JSONField(null=True)),
                ('dp_statistics', models.JSONField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DepositorSetupInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('is_complete', models.BooleanField(default=False)),
                ('user_step', models.CharField(choices=[('step_100', 'Step 1: Uploaded'), ('step_200', 'Step 2: Validated'), ('step_300', 'Step 3: Profiling Processing'), ('step_400', 'Step 4: Profiling Complete'), ('step_500', 'Step 5: Variable Defaults Confirmed'), ('step_600', 'Step 6: Epsilon Set'), ('error_9100', 'Error 1: Validation Failed'), ('error_9200', 'Error 2: Dataverse Download Failed'), ('error_9300', 'Error 3: Profiling Failed'), ('error_9400', 'Error 4: Create Release Failed')], default='step_100', max_length=128)),
                ('epsilon', models.FloatField(blank=True, null=True)),
                ('dataset_questions', models.JSONField(blank=True, null=True)),
                ('variable_ranges', models.JSONField(blank=True, null=True)),
                ('variable_categories', models.JSONField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Depositor Setup Data',
                'verbose_name_plural': 'Depositor Setup Data',
                'ordering': ('dataversefileinfo', '-created'),
            },
        ),
        migrations.CreateModel(
            name='ReleaseInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('object_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('epsilon_used', models.FloatField()),
                ('dp_release', models.JSONField()),
                ('analysis_plan', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='analysis.analysisplan')),
            ],
            options={
                'verbose_name': 'Release Information',
                'verbose_name_plural': 'Release Information',
                'ordering': ('dataset', '-created'),
            },
        ),
    ]
