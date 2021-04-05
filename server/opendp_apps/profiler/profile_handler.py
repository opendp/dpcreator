"""
Profile a data file
"""
import os
import pandas as pd

from django.conf import settings

from raven_preprocess.preprocess_runner import PreprocessRunner

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.model_helpers.basic_response import ok_resp, err_resp
from opendp_apps.dataset.models import DataSetInfo
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.static_vals_mime_types import get_data_file_separator


class ProfileHandler(BasicErrCheck):

    ERR_FAILED_TO_READ_DATASET = 'Failed to read the dataset.'
    ERR_DATASET_POINTER_NOT_SET = 'In order to profile the data, the "dataset_pointer" must be set.'

    def __init__(self, dataset_pointer, **kwargs):
        """
        Note: Use the staticmethods to call the initializers.
        Given a path to a dataset, profile it
        Optional args:
        dataset_object_id : DataSetInfo object_id. Save the profile to this object's data_profile attribute
        """

        # Either a filepath or Django FileField object
        self.dataset_pointer = dataset_pointer

        # Set to 'True' for a file available via a filepath
        self.dataset_is_filepath = kwargs.get(pstatic.KEY_DATASET_IS_FILEPATH, False)

        # Set to 'True' for a Django FileField object
        self.dataset_is_django_filefield = kwargs.get(pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD, False)

        self.data_profile = None    # Data profile information
        self.num_original_features = None

        # -------------------------------------
        # Optional
        # -------------------------------------
        # Indices of columns to profile. Default is the 1st 20 indices
        self.chosen_column_indices = kwargs.get('chosen_column_indices', settings.PROFILER_DEFAULT_COLUMN_INDICES)

        # If a DataSetInfo object is specified, the profile will be saved to the object
        self.dataset_info_object_id = kwargs.get(pstatic.KEY_DATASET_OBJECT_ID)
        self.dataset_info_object = None


        #start_row = kwargs.get('start_row')
        #num_rows = kwargs.get('num_rows', None)

        if self.check_parameters():
            self.run_profiler()
            self.save_to_dataset_info_object()

    def get_dataset_info_object(self):
        """Return the data profile as a Python dict"""
        assert self.has_error() is False, "Call .has_error() before using this method"
        return self.dataset_info_object


    def save_to_dataset_info_object(self):
        """If there's a connected DataSetInfo object, save the profile to it"""

        if self.has_error():
            return
        # If there's a connected DataSetInfo object,
        #  save the profile to it
        #
        if self.dataset_info_object:
            # print('type data_profile', type(self.data_profile))
            self.dataset_info_object.data_profile = self.data_profile
            self.dataset_info_object.save()


    def get_data_profile(self):
        """Return the data profile as a Python dict"""
        assert self.has_error() is False, "Call .has_error() before using this method"
        return self.data_profile

    def get_data_profile_as_json(self):
        """Return the data profile as a Python dict"""
        assert self.has_error() is False, "Call .has_error() before using this method"
        return self.data_profile



    def check_parameters(self):
        """Check parameters which includes distinguishing between a Django FileField using storages and filepath
        Reference to storage: backends, https://github.com/jschneier/django-storages/tree/master/storages/backends
        """
        if self.has_error():  # probably always False
            return False

        if not self.dataset_pointer:
            #user_msg = 'In order to profile the data, the "dataset_pointer" must be set.'
            self.add_err_msg(self.ERR_DATASET_POINTER_NOT_SET)
            return False

        # Is there a DataSetInfo object involved. If so, retrieve it
        #
        if self.dataset_info_object_id is not None:
            try:
                self.dataset_info_object = DataSetInfo.objects.get(object_id=self.dataset_info_object_id)
            except DataSetInfo.DoesNotExist:
                self.dataset_info_object = None
                user_msg = f'DataSetInfo object not found for id {self.dataset_info_object_id}'
                self.add_err_msg(user_msg)
                return False

        # Distinguish between a file path and an object
        #
        if self.dataset_is_django_filefield is True and self.dataset_is_filepath is True:
            user_msg = '"dataset_is_filepath" and "dataset_is_django_filefield" cannot both be True'
            self.add_err_msg(user_msg)
            return False

        if self.dataset_is_django_filefield is False and self.dataset_is_filepath is False:
            user_msg = '"dataset_is_filepath" and "dataset_is_django_filefield" cannot both be False'
            self.add_err_msg(user_msg)
            return False

        # Expecting a filepath to a readable dataset
        #
        if self.dataset_is_filepath:
            if not os.access(self.dataset_pointer, os.R_OK):
                self.add_err_msg(f'File is not readable: {self.dataset_pointer}')
                return False
            if not os.path.isfile(self.dataset_pointer):
                self.add_err_msg(f'This is not a file: {self.dataset_pointer}')
                return False

        #  Expecting a reference to a file stored on Azure, S3, etc.
        #
        if self.dataset_is_django_filefield:
            # print('>>>', dir(self.dataset_pointer))
            #try:
            if not self.dataset_pointer:
                user_msg = f'The dataset does not exist for the Django FileField storage at {self.dataset}'
                self.add_err_msg(user_msg)
                return False
            #except NotImplementedError:
            #    self.add_err_msg(f'.exists() method is not implemented for the Django FileField storage')
            #    return False

        return True


    def get_row_separator(self):
        """Needs some work; Get the 'sep' attribute for opening the dataset into a pandas dataframe"""
        if self.has_error():
            return err_resp('Previous error encountered')

        if isinstance(self.dataset_pointer, str):
            sep = get_data_file_separator(self.dataset_pointer)
        elif hasattr(self.dataset_pointer, 'name') and self.dataset_pointer.name:
            sep = get_data_file_separator(self.dataset_pointer.name)
        else:
            sep = get_data_file_separator(None)

        return ok_resp(sep)

    def get_dataset_as_dataframe(self):
        """Load the dataset into a Pandas dataframe
        TODO: this is set only for tabular files right now"""
        if self.has_error():
            return err_resp('Error already there!')

        sep_resp = self.get_row_separator()
        if not sep_resp.success:
            return
        sep_char = sep_resp.data

        df_read_params = dict(sep=sep_char)

        try:
            # Read the 1st row only; to determine the number of features/columns
            #
            df_for_size = pd.read_csv(self.dataset_pointer, nrows=1, **df_read_params)
            num_rows, self.num_original_features = df_for_size.shape
            # print(f'size: {df_for_size.shape}')

            # If there are more than the expected number of columns, for the full read, only use the 1st 20
            #
            if self.num_original_features > len(self.chosen_column_indices):
                df_read_params['usecols'] = self.chosen_column_indices

            # read the full file into the dataframe
            df = pd.read_csv(self.dataset_pointer, **df_read_params)
            return ok_resp(df)

        except pd.errors.EmptyDataError as err_obj:
            user_msg = f'{self.ERR_FAILED_TO_READ_DATASET} (EmptyDataError: {err_obj})'
            return err_resp(user_msg)
        except pd.errors.ParserError as err_obj:
            user_msg = f'{self.ERR_FAILED_TO_READ_DATASET} (ParserError: {err_obj})'
            return err_resp(user_msg)

    def run_profiler(self):
        """Run the profiler"""
        if self.has_error():
            return

        df_resp = self.get_dataset_as_dataframe()
        if not df_resp.success:
            self.add_err_msg(df_resp.message)
            return

        df = df_resp.data

        prunner = PreprocessRunner(dataframe=df)
        if prunner.has_error:
            self.add_err_resp(prunner.error_message)
            return

        self.data_profile = prunner.get_final_dict()

        self.prune_profile()

    def prune_profile(self):
        """Remove un-needed info from the profile
        TODO: Add these options directly into the TwoRavens preprocess code"""
        if self.has_error():
            return

        if 'variableDisplay' in self.data_profile:
            del self.data_profile['variableDisplay']


        #if ph.has_error():
        #    print(f'error: {ph.get_err_msg()}')
        #else:
        #   print('profiled!')
