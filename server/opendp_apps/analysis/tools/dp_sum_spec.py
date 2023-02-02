import logging

from django.conf import settings
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.measurements import make_base_laplace
from opendp.mod import OpenDPException
from opendp.mod import binary_search, enable_features
from opendp.transformations import \
    (make_bounded_resize,
     make_cast,
     make_clamp,
     make_impute_constant,
     make_select_column,
     make_split_dataframe, make_sized_bounded_sum)

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.utils.extra_validators import \
    (validate_float,
     validate_int_greater_than_zero,
     validate_min_max,
     validate_fixed_value_against_min_max,
     validate_missing_val_handlers,
     validate_type_numeric)

enable_features("floating-point", "contrib")

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DPSumSpec(StatSpec):
    """
    Initiate with dict of properties. Example of needed properties:

    spec_props = dict(var_name="hours_sleep",
                      col_index=3,
                      variable_info=dict(min=0, max=24, type=VAR_TYPE_FLOAT),
                      statistic=DP_SUM,
                      dataset_size=365,
                      epsilon=0.5,
                      cl=CL_95.
                      fixed_value=1)
    """
    STATISTIC_TYPE = astatic.DP_SUM

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_LAPLACE_MECHANISM

    def get_stat_specific_validators(self) -> dict:
        """
        Update self.prop_validators to include validators specific to the subclass
        @return:
        """
        return dict(var_type=validate_type_numeric,
                    dataset_size=validate_int_greater_than_zero,
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
        For additional checking after validation
        """
        if self.has_error():
            return

    def check_scale(self, scale, preprocessor, dataset_distance, epsilon):
        """
        Return T/F
        :param scale:
        :param preprocessor:
        :param dataset_distance:
        :param epsilon:
        :return:
        """
        if self.has_error():
            return

        return (preprocessor >> make_base_laplace(scale)).check(dataset_distance, epsilon)

    def get_preprocessor(self):
        """Preprocessor for DP Sum (float)"""
        if self.has_error():
            return None

        # Have we already already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        # Build the preprocessor!
        #
        preprocessor = (
                make_select_column(self.col_index, TOA=str) >>
                make_cast(TIA=str, TOA=float) >>
                make_impute_constant(constant=self.fixed_value) >>
                make_clamp(bounds=self.get_bounds()) >>
                make_bounded_resize(size=self.dataset_size, bounds=self.get_bounds(), constant=self.fixed_value) >>
                make_sized_bounded_sum(size=self.dataset_size, bounds=self.get_bounds())
        )

        self.scale = binary_search(lambda s: self.check_scale(s, preprocessor, self.max_influence, self.epsilon), bounds=(0.0, 1000.0))
        preprocessor = preprocessor >> make_base_laplace(self.scale)

        # keep a pointer to the preprocessor to re-use for .run_chain(...)
        self.preprocessor = preprocessor

        return preprocessor

    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence interval as alpha"""
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
        Calculate the DP Sum!

        Example:
        # Note "\t" is for a tabular file
        `dp_sum_spec.run_chain([0, 1, 2, 3], file_obj, sep_char="\t")`

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
            self.add_err_msg('DPSumSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
            return

        try:
            parse_dataframe = make_split_dataframe(separator=sep_char,
                                                   col_names=column_names)

            computation_chain = parse_dataframe >> self.preprocessor

            self.value = computation_chain(file_obj.read())

        except OpenDPException as ex_obj:
            logger.exception(ex_obj)
            self.add_err_msg(f'{ex_obj.message} (OpenDPException)')
            return False
        except Exception as ex_obj:
            logger.exception(ex_obj)
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        logger.info((f"Epsilon: {self.epsilon}"
                     f"\nColumn name: {self.variable}"
                     f"\nColumn index: {self.col_index}"
                     f"\nColumn accuracy_val: {self.accuracy_val}"
                     f"\nColumn accuracy_msg: {self.accuracy_msg}"
                     f"\n\nDP Sum: {self.value}"))

        return True
