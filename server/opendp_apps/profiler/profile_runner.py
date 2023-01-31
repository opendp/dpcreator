"""
Read and Profile a File.
"""
import logging
import os

from django.conf import settings
from django.db.models.fields.files import FieldFile

from opendp_apps.analysis.models import DepositorSetupInfo
from opendp_apps.dataset import static_vals as dstatic
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.csv_reader import CsvReader
from opendp_apps.profiler.dataset_info_updater import DataSetInfoUpdater
from opendp_apps.profiler.variable_info import VariableInfoHandler

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ProfileRunner(BasicErrCheck):
    """Given a filepath and optional DataSetInfo object id """

    def __init__(self, dataset_pointer, max_num_features=None, **kwargs):
        """
        Note: Use the staticmethods to call this __init__ method.
        Given a path to a dataset, profile it
        Optional args:
        dataset_object_id : DataSetInfo object_id. Save the profile to this object's data_profile attribute
        """
        #
        logger.info(f'Init ProfileRunner dataset_pointer: {dataset_pointer}')

        self.dataset_pointer = dataset_pointer  # Either a filepath or Django FileField object
        self.max_num_features = max_num_features  # None indicates no limit

        self.dataset_is_django_filefield = kwargs.get(pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD, False)

        # If a DataSetInfo object is specified, the profile will be saved to the object
        self.dataset_info_object_id = kwargs.get(pstatic.KEY_DATASET_OBJECT_ID)

        # Set to False depending on an answer to question about whether number of row may be made public
        self.save_row_count = kwargs.get(pstatic.KEY_SAVE_ROW_COUNT, True)

        # ------------------------------
        # To be set/calculated
        # ------------------------------
        # Used if a DataSetInfo object is specified
        self.dataset_info = None
        self.dataset_info_updater = None
        self.ds_pointer_for_pandas = None

        self.dataframe = None
        # self.num_original_features = None
        self.num_variables = None
        self.data_profile = None  # Data profile information

        # Set to 'True' for a file available via a filepath
        # self.dataset_is_filepath = kwargs.get(pstatic.KEY_DATASET_IS_FILEPATH, False)

        # Set to 'True' for a Django FileField object
        # self.dataset_is_django_filefield = kwargs.get(pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD, False)

        logger.info('Run basic checks...')
        self.run_basic_checks()
        logger.info('Basic checks complete!')
        self.run_profile_process()

    def add_err_msg(self, err_msg):
        """Add an error message and update the DepositorSetupInfo status"""
        super().add_err_msg(err_msg)
        self.set_depositor_info_status(DepositorSetupInfo.DepositorSteps.STEP_9300_PROFILING_FAILED)

    def set_depositor_info_status(self, new_step: DepositorSetupInfo.DepositorSteps) -> bool:
        """Update the status on the DepositorSetupInfo object.
        Only available if the dataset_info_object is populated"""
        if not self.dataset_info:
            return

        # Update the step
        self.dataset_info.depositor_setup_info.set_user_step(new_step)

        # save it
        self.dataset_info.depositor_setup_info.save()

    def run_basic_checks(self):
        """
        Run some basic error checking
        """
        # (1) Optional: Retrieve the DataSetInfo object and set the DataSetInfoUpdater
        #
        if self.dataset_info_object_id:
            try:
                self.dataset_info = DataSetInfo.objects.get(object_id=self.dataset_info_object_id)
            except DataSetInfo.DoesNotExist:
                self.add_err_msg(dstatic.ERR_MSG_DATASET_INFO_NOT_FOUND)
                return

            self.dataset_info_updater = DataSetInfoUpdater(self.dataset_info)

        # Is the dataset_pointer correct?
        #
        if self.dataset_is_django_filefield:
            # dataset pointer is a Django FileField
            if not isinstance(self.dataset_pointer, FieldFile):
                user_msg = f'{pstatic.ERR_MSG_DATASET_POINTER_NOT_FIELDFILE}'
                self.add_err_msg(user_msg)
                return
            elif not self.dataset_pointer:
                user_msg = (f'{pstatic.ERR_MSG_SOURCE_FILE_DOES_NOT_EXIST}'
                            f' {self.dataset_info} ({self.dataset_info.object_id})')
                self.add_err_msg(user_msg)
                return

            elif not hasattr(self.dataset_pointer, 'path'):
                # Fix for S3, etc.!!!
                user_msg = f'The Django FileField path was not found.'
                self.add_err_msg(user_msg)
                return
            else:
                self.ds_pointer_for_pandas = self.dataset_pointer.path
        else:
            # Assume dataset_pointer is a filepath
            if not os.access(self.dataset_pointer, os.R_OK):
                self.add_err_msg(f'File is not readable: {self.dataset_pointer}')
                return
            elif not os.path.isfile(self.dataset_pointer):
                self.add_err_msg(f'This is not a file: {self.dataset_pointer}')
                return
            else:
                self.ds_pointer_for_pandas = self.dataset_pointer

    def run_profile_process(self):
        """
        Run through the setup and profile process
        """
        logger.info('-- run_profile_process --')

        if self.has_error():
            return

        # (1) Does the profile already exist? Yes, then stop here
        #
        logger.info('(1) Does the profile already exist?')
        if self.dataset_info and self.dataset_info.data_profile and \
                self.dataset_info.profile_variables:
            #
            # Profile is already done! Return!
            self.data_profile = self.dataset_info.data_profile
            logger.info('Profile exists. All done.')
            return

        logger.info('No profile. Go make one')

        # (2) Open the dataframe
        #
        logger.info('(2) Read the data')
        try:
            self.dataframe = CsvReader(self.ds_pointer_for_pandas, column_limit=self.max_num_features).read()
        except UnicodeDecodeError as ex_obj:
            user_msg = f'Failed to open file due to UnicodeDecodeError. ({ex_obj})'
            self.add_err_msg(user_msg)
            logger.info(f'Failed to open file {user_msg}')
            return
        except Exception as ex:
            user_msg = f'File reading error. {ex}'
            self.add_err_msg(user_msg)
            logger.info(f'Failed to open file {user_msg}')
            return

        # (3) Run the profiler
        #
        logger.info('(2) Run the profiler')
        # Pre-profile: update user_step
        if self.dataset_info:
            if self.dataset_info.depositor_setup_info.user_step < DepositorSetupInfo.DepositorSteps.STEP_0300_PROFILING_PROCESSING:
                self.set_depositor_info_status(DepositorSetupInfo.DepositorSteps.STEP_0300_PROFILING_PROCESSING)
                logger.info('(2a) Update the profiler status')

        try:
            logger.info('(2b) It\'s running!')
            # Run the profile
            params = {pstatic.KEY_SAVE_ROW_COUNT: self.save_row_count}
            variable_info_handler = VariableInfoHandler(self.dataframe, **params)
            variable_info_handler.run_profile_process()

            # Get profiler values
            self.data_profile = variable_info_handler.data_profile
            self.num_variables = variable_info_handler.num_variables

        except Exception as ex:
            # Profiling failed: add error message
            user_msg = f'Profile runner error. {ex}'
            self.add_err_msg(user_msg)
            logger.info(f'(2c) !Profile failed!: {user_msg}')
            return

        # Profiling success: update DataSetInfo profile and user_step
        logger.info(f'(3) Profile complete!')
        if self.dataset_info:
            self.dataset_info_updater.save_data_profile(variable_info_handler.data_profile)
            if self.dataset_info.depositor_setup_info.user_step < DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE:
                self.set_depositor_info_status(DepositorSetupInfo.DepositorSteps.STEP_0400_PROFILING_COMPLETE)