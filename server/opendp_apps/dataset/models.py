import json
import logging
from collections import OrderedDict
from os.path import splitext

from django.apps import apps
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.utils.safestring import mark_safe
from polymorphic.models import PolymorphicModel

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.dataset.dataset_question_validators import \
    (validate_dataset_questions,
     validate_epsilon_questions)
from opendp_apps.dataset.depositor_setup_helpers import \
    (set_user_step_based_on_data,
     set_default_epsilon_delta_from_questions)
from opendp_apps.dataverses.models import RegisteredDataverse
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp, BasicResponse
from opendp_apps.model_helpers.models import \
    (TimestampedModelWithUUID, )
from opendp_apps.profiler.static_vals_mime_types import get_mime_type
# Temp workaround!!! See Issue #300
# https://github.com/opendp/dpcreator/issues/300
from opendp_apps.utils.camel_to_snake import camel_to_snake
# from opendp_apps.dataset.models import DepositorSetupInfo
from opendp_apps.utils.extra_validators import validate_not_negative, validate_epsilon_or_none
from opendp_apps.utils.variable_info_formatter import format_variable_info

logger = logging.getLogger(settings.DEFAULT_LOGGER)

UPLOADED_FILE_STORAGE = FileSystemStorage(location=settings.UPLOADED_FILE_STORAGE_ROOT)


class DepositorSetupInfo(TimestampedModelWithUUID):
    """
    Variable related to the Depositor Setup process
    """

    class DepositorSteps(models.TextChoices):
        """
        Enumeration for different statuses during depositor process
        """
        STEP_0000_INITIALIZED = 'step_000', 'Step 0: Initialized'
        STEP_0100_UPLOADED = 'step_100', 'Step 1: Uploaded'
        STEP_0200_VALIDATED = 'step_200', 'Step 2: Validated'  # done automatically for Dataverse use case
        STEP_0300_PROFILING_PROCESSING = 'step_300', 'Step 3: Profiling Processing'
        STEP_0400_PROFILING_COMPLETE = 'step_400', 'Step 4: Profiling Complete'
        STEP_0500_VARIABLE_DEFAULTS_CONFIRMED = 'step_500', 'Step 5: Variable Defaults Confirmed'
        STEP_0600_EPSILON_SET = 'step_600', 'Step 6: Epsilon Set'
        # Error statuses should begin with 9
        STEP_9100_VALIDATION_FAILED = 'error_9100', 'Error 1: Validation Failed'
        STEP_9200_DATAVERSE_DOWNLOAD_FAILED = 'error_9200', 'Error 2: Dataverse Download Failed'
        STEP_9300_PROFILING_FAILED = 'error_9300', 'Error 3: Profiling Failed'
        STEP_9400_CREATE_RELEASE_FAILED = 'error_9400', 'Error 4: Create Release Failed'

    # User who initially added/uploaded data
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)

    # Set on save
    is_complete = models.BooleanField(default=False,
                                      help_text='auto-populated on save')

    # Track workflow based on DepositorSteps
    user_step = models.CharField(max_length=128,
                                 choices=DepositorSteps.choices,
                                 default=DepositorSteps.STEP_0000_INITIALIZED)

    # Populated from the UI
    dataset_questions = models.JSONField(null=True,
                                         blank=True,
                                         validators=[validate_dataset_questions])

    epsilon_questions = models.JSONField(null=True,
                                         blank=True,
                                         validators=[validate_epsilon_questions])

    unverified_data_profile = models.JSONField(help_text='Unverified data profile',
                                               default=None,
                                               null=True,
                                               blank=True,
                                               encoder=DjangoJSONEncoder)

    # Includes variable ranges and categories
    data_profile = models.JSONField(null=True, blank=True)

    #
    # Epsilon related fields
    #
    default_epsilon = models.FloatField(null=True,
                                        blank=True,
                                        help_text='Default based on answers to epsilon_questions.',
                                        validators=[validate_epsilon_or_none])

    epsilon = models.FloatField(null=True, blank=True,
                                help_text=('Used for OpenDP operations, starts as the "default_epsilon"'
                                           ' value but may be overridden by the user.'),
                                validators=[validate_epsilon_or_none])

    #
    # Delta related fields
    #
    default_delta = models.FloatField(null=True,
                                      blank=True,
                                      default=astatic.DELTA_0,
                                      help_text='Default based on answers to epsilon_questions.',
                                      validators=[validate_not_negative])

    delta = models.FloatField(null=True,
                              blank=True,
                              default=astatic.DELTA_0,
                              help_text=('Used for OpenDP operations, starts as the "default_delta"'
                                         ' value but may be overridden by the user.'),
                              validators=[validate_not_negative])

    confidence_level = models.FloatField(choices=astatic.CL_CHOICES,
                                         default=astatic.CL_95,
                                         help_text=('Used for OpenDP operations, starts as the "default_delta"'
                                                    ' value but may be overridden by the user.'))

    class WizardSteps(models.TextChoices):
        """
        Enumeration for different statuses during depositor process
        """
        STEP_0100_FILE_UPLOAD = 'step_100', 'Step 1: File Upload'
        STEP_0200_DATASET_QUESTIONS = 'step_200', 'Step 2: Dataset Questions'
        STEP_0300_CONFIRM_VARIABLES = 'step_300', 'Step 3: Confirm Variables'
        STEP_0400_SET_EPSILON = 'step_400', 'Step 4: Set Epsilon'

    wizard_step = models.CharField(max_length=128,
                                   choices=WizardSteps.choices,
                                   default=WizardSteps.STEP_0100_FILE_UPLOAD)

    @property
    def dataset_size(self):
        """Return the dataset_size from the DataSetInfo.variable_info"""
        ds_info = self.get_dataset_info()

        dataset_size_info = ds_info.get_dataset_size()

        if dataset_size_info.success:
            return dataset_size_info.data

        return None

    class Meta:
        verbose_name = 'Depositor Setup Data'
        verbose_name_plural = 'Depositor Setup Data'
        ordering = ('-created',)

    def __str__(self):
        ds_info = self.get_dataset_info()
        if ds_info:
            return f'{ds_info} - {self.user_step}'

        return f'{self.object_id} - {self.user_step}'

    def save(self, *args, **kwargs):
        """Override the save method to set the user_step based on the data"""
        if self.data_profile:
            self.data_profile = format_variable_info(self.data_profile)

        set_user_step_based_on_data(self)
        set_default_epsilon_delta_from_questions(self)

        # Specifically for this model, we are overriding the update method with an explicit list of
        # update_fields, so we need to set the updated field manually.
        # All other models will be updated without this step due to the auto_now option from the parent class.
        self.updated = timezone.now()
        super(DepositorSetupInfo, self).save(*args, **kwargs)

    @mark_safe
    def name(self):
        return str(self)

    def get_dataset_info(self):
        """
        Access a DataSetInfo object, either dataversefileinfo or uploadfileinfo
        # Workaround for https://github.com/opendp/dpcreator/issues/257
        """
        if hasattr(self, 'ds_info'):
            if hasattr(self.ds_info, 'uploadfileinfo'):
                return self.ds_info.uploadfileinfo
            elif hasattr(self.ds_info, 'dataversefileinfo'):
                return self.ds_info.dataversefileinfo
            else:
                return self.ds_info

        return None

    def set_user_step(self, new_step: DepositorSteps) -> bool:
        """Set a new user step. Does *not* save the object."""
        assert isinstance(new_step, DepositorSetupInfo.DepositorSteps), \
            "new_step must be a valid choice in DepositorSteps"
        self.user_step = new_step
        return True

    def set_wizard_step(self, new_wizard_step: WizardSteps) -> bool:
        """Set a new user step. Does *not* save the object."""
        assert isinstance(new_wizard_step, DepositorSetupInfo.WizardSteps), \
            "new_step must be a valid choice in DepositorSteps"
        self.wizard_step = new_wizard_step
        return True

    @mark_safe
    def data_profile_view(self):
        """For admin display of the variable info"""
        if not self.data_profile:
            return 'n/a'

        try:
            info_str = json.dumps(self.data_profile, indent=4)
            return f'<pre>{info_str}</pre>'
        except Exception as ex_obj:
            return f'Failed to convert to JSON string {ex_obj}'

    @mark_safe
    def user_step_label(self) -> str:
        """Return the label for the user step"""
        return self.user_step.get_user_step_display()


class DataSetInfo(TimestampedModelWithUUID, PolymorphicModel):
    """
    Base type for table that either holds DV data
    or a file upload
    """
    # user who initially added/uploaded data
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT)

    class SourceChoices(models.TextChoices):
        UserUpload = 'upload', 'Upload'
        Dataverse = 'dataverse', 'Dataverse'

    name = models.CharField(max_length=128)

    source = models.CharField(max_length=128,
                              choices=SourceChoices.choices)

    source_file = models.FileField(storage=UPLOADED_FILE_STORAGE,
                                   upload_to='source-file/%Y/%m/%d/',
                                   blank=True, null=True)

    depositor_setup_info = models.OneToOneField(DepositorSetupInfo,
                                                related_name='ds_info',
                                                null=True,
                                                # blank=True,
                                                on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Dataset Information'
        verbose_name_plural = 'Dataset Information'
        ordering = ('name', '-created')

    def __str__(self):
        return self.name

    @staticmethod
    def delete_source_file(dataset_info) -> BasicResponse:
        """
        Delete the source_file, if it exists
        - Returns a BasicResponse object with success = True if file is deleted
           or not set to start with
        """
        if not dataset_info.source_file:
            # No source file
            return ok_resp(True)

        # source_file found, delete it
        try:
            dataset_info.source_file.delete()
            dataset_info.save()
            return ok_resp(True)
        except OSError as err_obj:
            # OSError found
            return err_resp(f'Failed to delete source_file. ({err_obj})')
        except Exception as err_obj:
            # General exception found
            return err_resp(f'Failed to delete source_file. ({err_obj})')

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(id=self.id,
                    creator=str(self.creator),
                    source=str(self.source),
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info

    def save(self, *args, **kwargs):
        """Make sure there is a DepositorSetupInfo object"""
        # print('DataSetInfo.save()')
        initial_link_of_depositor_setup_info = False
        if not self.depositor_setup_info:
            # Set default DepositorSetupInfo object
            initial_link_of_depositor_setup_info = True
            dsi = DepositorSetupInfo.objects.create(creator=self.creator)
            self.depositor_setup_info = dsi

        # Specifically for this model, we are overriding the update method with an explicit list of
        # update_fields, so we need to set the updated field manually.
        # All other models will be updated without this step due to the auto_now option from the parent class.
        self.updated = timezone.now()

        super(DataSetInfo, self).save(*args, **kwargs)

        if initial_link_of_depositor_setup_info is True:
            # Save again to correct set the user_step on the DepositorSetupInfo object
            self.depositor_setup_info.save()

    @property
    def status(self):
        """
        Return the user_step object
        """
        try:
            return self.depositor_setup_info.user_step
        except DepositorSetupInfo.DoesNotExist:
            return DepositorSetupInfo.DepositorSteps.STEP_0000_INITIALIZED

    @property
    def status_name(self):
        """
        Return the user_step label
        """
        try:
            return self.depositor_setup_info.user_step.label
        except DepositorSetupInfo.DoesNotExist:
            return DepositorSetupInfo.DepositorSteps.STEP_0000_INITIALIZED.label

    # @property
    # def depositor_setup_info(self):
    #    """shortcut to access the DepositorSetupInfo"""
    #    return self.get_depositor_setup_info()

    def is_dataverse_file_info(self):
        """Is this an instance of a DataverseFileInfo object?"""
        if hasattr(self, 'get_real_instance') is False:
            return False

        return isinstance(self.get_real_instance(), DataverseFileInfo)

    def is_upload_file_info(self):
        """Is this an instance of an UploadFileInfo object?"""
        if hasattr(self, 'get_real_instance') is False:
            return False

        return isinstance(self.get_real_instance(), UploadFileInfo)

    # def get_depositor_setup_info(self):
    #    """Hack; need to address https://github.com/opendp/dpcreator/issues/257"""
    #    try:
    #        return self.get_real_instance().depositor_setup_info
    #    except AttributeError as err_obj:
    #        user_msg = (f'Unknown DataSetinfo type. No access to depositor_setup_info.'
    #                    f' depositor_setup_info. class:'
    #                    f' {self.get_real_instance().__class__}. err: {err_obj}')
    #        logger.error(user_msg)
    #       raise AttributeError(user_msg)

    def get_dataset_size(self) -> BasicResponse:
        """Retrieve the rowCount index from the data_profile -- not always available"""
        if not self.data_profile:
            return err_resp('Data profile not available')

        if 'dataset' not in self.data_profile:
            return err_resp('Dataset information not available in profile')

        if 'rowCount' not in self.data_profile['dataset']:
            return err_resp('"rowCount" information not available in profile.')

        row_count = self.data_profile['dataset']['rowCount']
        if row_count is None:
            return err_resp('"rowCount" information not available in profile (id:2')

        return ok_resp(self.data_profile['dataset']['rowCount'])

    def get_variable_order(self, as_indices=False) -> BasicResponse:
        """
        Retrieve the variableOrder list from the data_profile
         Example data structure:
          {"dataset":{
              "rowCount":6610,
              "variableCount":20,
              "variableOrder":[
                 [0, "ccode"],
                 [1, "country"],
                 [2, "cname" ],
                ]
            }
            etc
          }

        :param as_indices, if True, return [0, 1, 2], etc.
        """
        if not self.data_profile:
            return err_resp('Data profile not available')

        if 'dataset' not in self.data_profile:
            return err_resp('Dataset information not available in profile')

        if 'variableOrder' not in self.data_profile['dataset']:
            return err_resp('"variableOrder" information not available in profile (id:2')

        variable_order = self.data_profile['dataset']['variableOrder']

        if as_indices:
            try:
                return ok_resp([idx for idx, _var_name in variable_order])
            except Exception as ex_obj:
                user_msg = (f'"variableOrder" information not in proper format: {variable_order}'
                            f' (exception: {ex_obj}')
                return err_resp(user_msg)

        return ok_resp(variable_order)

    def get_variable_index(self, var_name: str) -> BasicResponse:
        """Retrieve the variable index from the data_profile for a specific variable name
         Example data structure:
          {"dataset":{
              "rowCount":6610,
              "variableCount":20,
              "variableOrder":[
                 [0, "ccode"],
                 [1, "country"],
                 [2, "cname" ],
                ]
            }
            etc
          }

        :param var_name - variable name, e.g. "cname" would return 1
        """
        if not self.data_profile:
            return err_resp('Data profile not available')

        if 'dataset' not in self.data_profile:
            return err_resp('Dataset information not available in profile')

        if 'variableOrder' not in self.data_profile['dataset']:
            return err_resp('"variableOrder" information not available in profile (id:2')

        variable_order = self.data_profile['dataset']['variableOrder']
        if not variable_order:
            return err_resp('Bad "variableOrder" information in profile.')

        try:
            for idx, feature in self.data_profile['dataset']['variableOrder']:
                if feature == var_name:
                    return ok_resp(idx)
                elif feature == camel_to_snake(var_name):  # Temp workaround!!!
                    # Temp workaround!!! See Issue #300
                    # https://github.com/opendp/dpcreator/issues/300
                    return ok_resp(idx)

        except ValueError:
            return err_resp('Bad "variableOrder" information in profile. (id:3)')

        return err_resp(f'Index not found for variable "{var_name}"')

    def get_profile_variables(self):
        """Return the data profile and DataSetInfo object_id as an OrderedDict or None."""
        if not self.data_profile:
            return None

        od = OrderedDict(dict(object_id=self.object_id))
        od.update(self.data_profile)

        return od

    def data_profile_as_dict(self):
        """Return the dataprofile as a dict or None."""
        if not self.data_profile:
            return None

        try:
            if isinstance(self.data_profile, str):  # messy; decode escaped string to JSON string
                load1 = json.loads(self.data_profile,
                                   object_pairs_hook=OrderedDict)
            else:
                load1 = self.data_profile

            if isinstance(load1, dict):
                return load1

            return json.loads(load1, object_pairs_hook=OrderedDict)  # JSON string to OrderedDict

        except json.JSONDecodeError:
            return None

    def data_profile_as_json_str(self):
        """
        Return the dataprofile as a dict or None.
        """
        if not self.data_profile:
            return None

        try:
            return json.loads(self.data_profile)
        except json.JSONDecodeError:
            return None

    def is_dataverse_dataset(self) -> bool:
        """Shortcut to check if it's a Dataverse dataset"""
        return self.source == DataSetInfo.SourceChoices.Dataverse

    def get_dataverse_user(self):
        """
        Check if this is a Dataverse dataset, if so return the DataverseUser
        """
        if self.is_dataverse_dataset():
            return self.dataversefileinfo.get_dataverse_user()
        return None

    def get_dataverse_file_info(self):
        """
        Check if this is a Dataverse dataset, if so return the DataverseFileInfo
        """
        if self.is_dataverse_dataset():
            return self.dataversefileinfo
        return None

    @mark_safe
    def data_profile_display(self):
        """For admin display of the variable info"""
        if not self.depositor_setup_info:
            return 'n/a'

        return self.depositor_setup_info.data_profile_display()


class DataverseFileInfo(DataSetInfo):
    """
    Refers to a DV file from within a DV dataset
    """
    dv_installation = models.ForeignKey(RegisteredDataverse, on_delete=models.PROTECT)
    dataverse_file_id = models.IntegerField()
    dataset_doi = models.CharField(max_length=255)
    file_doi = models.CharField(max_length=255, blank=True)
    dataset_schema_info = models.JSONField(null=True, blank=True)
    file_schema_info = models.JSONField(null=True, blank=True)

    class Meta:
        verbose_name = 'Dataverse File Information'
        verbose_name_plural = 'Dataverse File Information'
        ordering = ('name', '-created')
        constraints = [
            models.UniqueConstraint(fields=['dv_installation', 'dataverse_file_id'],
                                    name='unique Dataverse file')
        ]

    def __str__(self):
        return f'{self.name} ({self.dv_installation.name})'

    def save(self, *args, **kwargs):
        """
        Future: is_complete can be auto-filled based on either field values or the STEP
        Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
              depending on the data
        """
        if not self.name:
            self.name = f'{self.dataset_doi} ({self.dv_installation})'

        self.source = DataSetInfo.SourceChoices.Dataverse

        super(DataverseFileInfo, self).save(*args, **kwargs)

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(id=self.id,
                    name=self.name,
                    creator=str(self.creator),
                    source=str(self.source),
                    dv_installation=self.dv_installation,
                    dataverse_file_id=self.dataverse_file_id,
                    dataset_doi=self.dataset_doi,
                    file_doi=self.file_doi,
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info

    def get_dataverse_user(self):
        """Convenience method to retrieve the Dataverse User associated with this dataset"""

        dv_user_model = apps.get_model(app_label='user', model_name='DataverseUser')
        try:
            return dv_user_model.objects.get(user=self.creator, dv_installation=self.dv_installation)
        except dv_user_model.DoesNotExist:
            return None


class UploadFileInfo(DataSetInfo):
    """Used to handle files uploaded by the user"""

    def get_file_type(self):
        """
        (hack) Return the file type based on the extension
        TODO: save this as an attribute
        """
        _filename, file_extension = splitext(self.name)
        return get_mime_type(file_extension, '(unknown file type)')

    def save(self, *args, **kwargs):
        # print('UploadFileInfo.save()')

        # Future: is_complete can be auto-filled based on either field values or the STEP
        #   Note: it's possible for either variable_ranges or variable_categories to be empty, e.g.
        #       depending on the data
        #
        self.source = DataSetInfo.SourceChoices.UserUpload

        super(UploadFileInfo, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Upload File Information'
        verbose_name_plural = 'Upload File Information'
        ordering = ('name', '-created')

    def __str__(self):
        return f'{self.name} ({self.source})'

    def as_dict(self):
        """
        Return as dict
        """
        info = dict(self.id,
                    name=self.name,
                    creator=str(self.creator),
                    source=str(self.source),
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex)

        return info


# ----------------------------------------------------------------------
# post_delete used for removing depositor_setup_info OneToOneField's
# ----------------------------------------------------------------------
@receiver(post_delete, sender=DataSetInfo)
def post_delete_depositor_info_from_dataset_info(sender, instance, *args, **kwargs):
    # Delete the DepositorSetupInfo object -- a OneToOneField
    try:
        if instance.depositor_setup_info:
            instance.depositor_setup_info.delete()
    except DepositorSetupInfo.DoesNotExist:
        pass
        # print('Does not exist. Already deleted.')


@receiver(post_delete, sender=DataverseFileInfo)
def post_delete_depositor_info_from_dv_file_info(sender, instance, *args, **kwargs):
    # Delete the DepositorSetupInfo object -- a OneToOneField
    try:
        if instance.depositor_setup_info:
            instance.depositor_setup_info.delete()
    except DepositorSetupInfo.DoesNotExist:
        pass
        print('Does not exist. Already deleted.')


@receiver(post_delete, sender=UploadFileInfo)
def post_delete_depositor_info_from_upload_file_info(sender, instance, *args, **kwargs):
    # Delete the DepositorSetupInfo object -- a OneToOneField
    try:
        if instance.depositor_setup_info:  # just in case user is not specified
            instance.depositor_setup_info.delete()
    except DepositorSetupInfo.DoesNotExist:
        pass
        # print('Does not exist. Already deleted.')
