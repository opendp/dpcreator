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

class ProfileHandler(BasicErrCheck):

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

        # -------------------------------------
        # Optional
        # -------------------------------------
        # Indices of columns to profile. Default is the 1st 20 indices
        self.chosen_column_indices = kwargs.get('chosen_column_indices', settings.DEFAULT_COLUMN_INDICES)

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
            return

        # Is there a DataSetInfo object involved. If so, retrieve it
        #
        if self.dataset_info_object_id is not None:
            try:
                self.dataset_info_object = DataSetInfo.objects.get(object_id=self.dataset_info_object_id)
            except DataSetInfo.DoesNotExist:
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
            try:
                if self.dataset_pointer.exists() is False:
                    user_msg = f'The dataset does not exist for the Django FileField storage at {self.dataset}'
                    self.add_err_msg(user_msg)
                    return False
            except NotImplementedError:
                self.add_err_msg(f'.exists() method is not implemented for the Django FileField storage')
                return False

        return True

    def get_dataset_as_dataframe(self):
        """Load the dataset into a Pandas dataframe
        TODO: this is set only for tabular files right now
        """
        if self.has_error():
            return err_resp('Error already there!')

        try:
            df = pd.read_csv(self.dataset_pointer,
                             #sep='\t',
                             # lineterminator='\r',
                             usecols=self.chosen_column_indices,
                             #skiprows=range(1, start_row),
                             # skip rows range starts from 1 as 0 row is the header
                             #nrows=num_rows
                            )
            return ok_resp(df)
        except:
            return err_resp('Failed to read file')

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




    @staticmethod
    def run_profile_by_filefield(filefield, **kwargs):
        """Run the profiler using a valid filepath"""
        params = {pstatic.KEY_DATASET_IS_DJANGO_FILEFIELD: True}
        if pstatic.KEY_DATASET_OBJECT_ID in kwargs:
            params[pstatic.KEY_DATASET_OBJECT_ID] = kwargs[pstatic.KEY_DATASET_OBJECT_ID]

        ph = ProfileHandler(dataset_pointer=filefield, **params)
        return ph

        #if ph.has_error():
        #    print(f'error: {ph.get_err_msg()}')
        #else:
        #   print('profiled!')
