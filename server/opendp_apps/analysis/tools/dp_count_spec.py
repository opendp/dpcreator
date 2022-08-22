"""
Wrapper class for DP Count functionality
"""
import logging

from django.conf import settings
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.meas import make_base_geometric
from opendp.mod import OpenDPException
from opendp.mod import binary_search, enable_features
from opendp.trans import \
    (make_cast,
     make_count,
     make_impute_constant,
     make_select_column,
     make_split_dataframe)

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.stat_spec import StatSpec

enable_features("floating-point", "contrib")

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DPCountSpec(StatSpec):
    """
    Initiate with dict of properties. Example of needed properties:

    spec_props = {'variable': 'age',
              'col_index': 1,
              'statistic': astatic.DP_COUNT,
              'epsilon': 1.0,
              'cl': astatic.CL_95,
              'variable_info': {'type': pstatic.VAR_TYPE_INTEGER},
              }
    """
    STATISTIC_TYPE = astatic.DP_COUNT

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_GEOMETRIC_MECHANISM

    def get_stat_specific_validators(self) -> dict:
        """
        Update self.prop_validators to include validators specific to the subclass
        @return: dict
        """
        # No additional validators
        return {}

    def run_01_initial_transforms(self):
        """
        Missing value handling, if a fixed_value is given, make it string
        """
        pass

    def run_03_custom_validation(self):
        """
        This is a place for initial checking/transformations
        such as making sure values are floats
        Example:
        self.check_numeric_fixed_value()
        """
        # Custom validation not needed
        pass

    def check_scale(self, scale, preprocessor, dataset_distance, epsilon):
        """
        Return T/F
        :param scale:
        :param preprocessor:
        :param dataset_distance:
        # :param epsilon:
        :return:
        """
        if self.has_error():
            return

        return (preprocessor >> make_base_geometric(scale)).check(dataset_distance, epsilon)

    def get_preprocessor(self):
        """DP Count preprocessor"""
        if self.has_error():
            return

        # Have we already already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        preprocessor = (
            # Selects a column of df, Vec<str>
                make_select_column(key=self.col_index, TOA=str) >>
                # Cast the column to str
                make_cast(TIA=str, TOA=str) >>
                # Impute missing values
                make_impute_constant('') >>  # Can this be an empty string?
                # Count!
                make_count(TIA=str)
        )

        self.scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon),
                                   bounds=(0.0, 1000.0))

        preprocessor = preprocessor >> make_base_geometric(self.scale)

        # keep a pointer to the preprocessor to re-use for .run_chain(...)
        self.preprocessor = preprocessor

        return preprocessor

    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence level alpha"""
        if self.has_error():
            return False

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        cl_alpha = self.get_confidence_level_alpha()
        if cl_alpha is None:
            # Error already saved
            return False
        self.accuracy_val = laplacian_scale_to_accuracy(self.scale, cl_alpha)

        # Note `self.accuracy_val` must bet set before using `self.get_accuracy_text()
        #
        self.accuracy_msg = self.get_accuracy_text()

        return True

    def run_chain(self, column_names, file_obj, sep_char=","):
        """
        Calculate the DP Count!

        Example:
        # Note "\t" is for a tabular file
        `dp_count_spec.run_chain([0, 1, 2, 3], file_obj, sep_char="\t")`

        @param column_names: Using a zero-based index of columns is preferred.
                    Examples: [0, 1, 2, 3] or ['a', 'b', 'c', 'd'] -- depends on your stat!
        @param file_obj: file like object to read data from
        @param sep_char:  separator from the object, default is "," for a .csv, etc
        @return: bool. if False: error messages are available through .get_err_msgs()
                                 or .get_error_msg_dict()
                       if True: results available through .value -- others params through
                                .get_success_msg_dict()
        """
        if not self.preprocessor:
            assert False, 'Please call is_chain_valid() before using "run_chain()!'

        self.value = None

        if self.has_error():
            return False

        if not isinstance(column_names, list):
            self.add_err_msg('DPMeanSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
            return

        try:
            parse_dataframe = make_split_dataframe(separator=sep_char,
                                                   col_names=column_names)

            computation_chain = parse_dataframe >> self.preprocessor

            self.value = computation_chain(file_obj.read())

        except OpenDPException as ex_obj:
            self.add_err_msg(f'{ex_obj.message} (OpenDPException)')
            return False

        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        logger.info((f"Epsilon: {self.epsilon}"
                     f"\nColumn name: {self.variable}"
                     f"\nColumn index: {self.col_index}"
                     f"\nColumn accuracy_val: {self.accuracy_val}"
                     f"\nColumn accuracy_message: {self.accuracy_msg}"
                     f"\n\nDP Count: {self.value}"))

        return True
