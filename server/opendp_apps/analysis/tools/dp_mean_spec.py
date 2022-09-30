"""
Calculate a DP Mean.
Note, the casting is str -> float.
Therefore all fields used in the calculation (min, max, etc) need to float

"""
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.meas import make_base_laplace
from opendp.mod import OpenDPException
from opendp.mod import binary_search, enable_features
from opendp.trans import \
    (make_bounded_resize,
     make_cast,
     make_clamp,
     make_impute_constant,
     make_select_column,
     make_sized_bounded_mean,
     make_split_dataframe)

enable_features("floating-point", "contrib")

from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.utils.extra_validators import \
    (validate_float,
     validate_min_max,
     validate_fixed_value_against_min_max,
     validate_missing_val_handlers,
     validate_int_greater_than_zero)

class DPMeanSpec(StatSpec):

    STATISTIC_TYPE = astatic.DP_MEAN

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_LAPLACE_MECHANISM

    def get_stat_specific_validators(self):
        """Set validators used for the DP Mean"""

        return dict(dataset_size=validate_int_greater_than_zero,
                    #
                    min=validate_float,
                    max=validate_float,
                    #
                    missing_values_handling=validate_missing_val_handlers)

    def run_01_initial_transforms(self):
        """
        Make sure values are consistently floats
        """
        if self.has_error():
            return

        if not self.floatify_int_values(['min', 'max', 'cl']):
            return

        # validate min/max
        if not self.validate_multi_values([self.min, self.max], validate_min_max, 'min/max'):
            return

        # Use the "impute_value" for missing values, make sure it's a float!
        #
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            # Convert the impute value to a float!
            if not self.cast_property_to_float('fixed_value'):
                return

            if not self.validate_multi_values([self.fixed_value, self.min, self.max],
                                              validate_fixed_value_against_min_max,
                                              'Is fixed value within min/max bounds?'):
                return

    def run_03_custom_validation(self):
        """
        There's no additional checking to do
        """
        if self.has_error():
            return


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

        return (preprocessor >> make_base_laplace(scale)).check(dataset_distance, epsilon)

    def get_preprocessor(self):
        """Preprocessor for DP Mean (float)"""
        if self.has_error():
            return None

        # Have we already already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        preprocessor = (
                # Selects a column of df, Vec<str>
                make_select_column(key=self.col_index, TOA=str) >>
                # Cast the column as Vec<Optional<Float>>
                make_cast(TIA=str, TOA=float) >>
                # Impute missing values to 0 Vec<Float>
                make_impute_constant(self.fixed_value) >>
                # Clamp age values
                make_clamp(self.get_bounds()) >>
                make_bounded_resize(self.dataset_size, self.get_bounds(), self.fixed_value) >>
                make_sized_bounded_mean(self.dataset_size, self.get_bounds())
        )

        self.scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon), bounds=(0.0, 1000.0))
        preprocessor = preprocessor >> make_base_laplace(self.scale)

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
        """
        self.accuracy_msg = (f"Releasing {self.statistic} for the variable {self.variable}."
                             f" With at least probability {self.get_cl_text()} the output {self.statistic}"
                             f" will differ from the true {self.statistic} by at"
                             f" most {self.accuracy_val} units."
                             f" Here the units are the same units the variable has in the dataset.")
        """
        return True

    def run_chain(self, column_names, file_obj, sep_char=","):
        """
        Calculate the DP Mean!

        Example:
        # Note "\t" is for a tabular file
        `dp_mean_spec.run_chain([0, 1, 2, 3], file_obj, sep_char="\t")`

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

        return True
