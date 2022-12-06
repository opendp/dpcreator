import logging

from django.conf import settings
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.meas import *
from opendp.mod import enable_features, binary_search_param, OpenDPException
from opendp.trans import *
from opendp.typing import *

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.utils.extra_validators import \
    (validate_not_none,
     validate_not_empty_or_none,
     validate_type_boolean,
     validate_missing_val_handlers,
     validate_bool_true_false,
     validate_histogram_bin_type_one_per_value,
     validate_fixed_value_in_categories)

enable_features("floating-point", "contrib")

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class DPHistogramBooleanSpec(StatSpec):
    """
    Create a Histogram using categorical (string) values.
    Requires "categories" to be specificed in the constructor
    """
    STATISTIC_TYPE = astatic.DP_HISTOGRAM  # _CATEGORICAL

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_GEOMETRIC_MECHANISM

    def get_stat_specific_validators(self) -> dict:
        """
        Update self.prop_validators to include validators specific to the subclass
        @return:
        """
        return dict(var_type=validate_type_boolean,
                    true_value=validate_not_empty_or_none,
                    false_value=validate_not_empty_or_none,
                    missing_values_handling=validate_missing_val_handlers)

    def run_01_initial_transforms(self):
        """
        Convert values to strings, where appropriate
        """
        if self.has_error():
            return

        if not self.validate_property('true_value', validate_not_empty_or_none):
            return

        if not self.validate_property('false_value', validate_not_empty_or_none):
            return

        '''
        if self.true_value is None:
            self.add_err_msg('The "true_value" must be set.')
            return

        if self.false_value is None:
            self.add_err_msg('The "true_value" must be set.')
            return
        '''
        # Make sure true_value and false_value aren't equal to each other
        #
        print('-- t3')
        if not self.validate_multi_values([self.true_value, self.false_value], validate_bool_true_false):
            return

        # Set the categories to the true and false values
        #
        self.categories = [self.true_value, self.false_value]

        # Stringify categorical values
        #
        updated_cats = []

        # Iterate through the categories, changing them to strings
        for idx, x in enumerate(self.categories):
            try:
                if not isinstance(x, str):
                    x = str(x)
                x = self._add_double_quotes(x)
                updated_cats.append(x)
            except NameError as _ex_obj:
                user_msg = 'Failed to convert category to string. (Failed category index {idx})'
                self.add_err_msg(user_msg)
                return

        self.categories = updated_cats

        # If the fixed_value is to be used, make sure it's valid
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:

            # Make sure the fixed value isn't None
            if not self.validate_property('fixed_value', validate_not_none):
                return

            # Double quote the fixed value and make sure it's a string
            if not isinstance(self.fixed_value, str):
                self.fixed_value = str(self.fixed_value)

            self.fixed_value = self._add_double_quotes(self.fixed_value)

            # ** not applying this next option, the fixed_value can be neither true/false **
            # Is the fixed value one of the categories?
            #if not self.validate_multi_values([self.fixed_value, self.categories],
            #                                  validate_fixed_value_in_categories,
            #                                  'fixed_value'):
            #    return

    def run_03_custom_validation(self):
        """
        No custom validation needed
        """
        pass

    def check_scale(self, scale, preprocessor):
        """
        TODO: Signature is wrong!!
        TODO: Why does this make sense?? Domain of int, etc.!!
        Return T/F
        :param scale:
        :param preprocessor:
        :return:
        """
        if self.has_error():
            return

        return preprocessor >> make_base_geometric(scale, D=VectorDomain[AllDomain[int]])

    def get_preprocessor(self):
        """
        Set up and return computation chain
        Note: Exceptions are caught via "is_chain_valid()"
        :return:
        """
        if self.has_error():
            return

        # Have we already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        preprocessor = (
                make_select_column(key=self.col_index, TOA=str) >>
                make_cast(TIA=str, TOA=str) >>
                make_impute_constant(self.fixed_value) >>
                make_count_by_categories(categories=self.categories, MO=L1Distance[int], TIA=str)
        )

        self.scale = binary_search_param(
            lambda s: self.check_scale(s, preprocessor), d_in=1, d_out=self.epsilon)
        preprocessor = preprocessor >> make_base_geometric(scale=self.scale, D=VectorDomain[AllDomain[int]])

        # keep a pointer to the preprocessor in case it's re-used
        self.preprocessor = preprocessor
        return preprocessor

    def set_accuracy(self):
        """
        Return the accuracy measure using Laplace and the confidence level alpha
        """
        if self.has_error():
            return False

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        cl_alpha = self.get_confidence_level_alpha()
        if cl_alpha is None:
            # Error already saved
            return False
        else:
            # This is for histograms, so divide alpha by the number of counts
            cl_alpha = cl_alpha / len(self.categories)

        self.accuracy_val = laplacian_scale_to_accuracy(self.scale, cl_alpha)

        # Note `self.accuracy_val` must bet set before using `self.get_accuracy_text()
        self.accuracy_msg = self.get_accuracy_text(template_name='analysis/dp_histogram_accuracy_default.txt')

        return True

    def run_chain(self, column_names, file_obj, sep_char=","):
        """
        Calculate the stats! See "dp_mean_spec.py" for an example of instantiation

        :param column_names, Example: [0, 1, 2, 3] or ['a', 'b', 'c', 'd'] -- depends on your stat!
                - In general using zero-based index of columns is preferred
        :param file_obj - file like object to read data from
        :param sep_char - separator from the object, default is "," for a .csv, etc

        :return bool -  False: error messages are available through .get_err_msgs()
                                or .get_error_msg_dict()
                        True: results available through .value -- others params through
                                .get_success_msg_dict()

        Example:
        # Note "\t" is for a tabular file
        `dp_mean_spec.run_chain([0, 1, 2, 3], file_obj, sep_char="\t")`
        """
        if not self.preprocessor:
            assert False, 'Please call is_chain_valid() before using "run_chain()!'

        self.value = None

        if self.has_error():
            return False

        if not isinstance(column_names, list):
            self.add_err_msg(
                'DPHistogramBooleanSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
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
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        # Remove double quotes from the categories as well as fixed value
        #
        fmt_categories = [self._remove_double_quotes(x) for x in self.categories] + ['uncategorized']
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            self.fixed_value = self._remove_double_quotes(self.fixed_value)

        # Show warning if category count doesn't match values count
        if len(fmt_categories) > len(self.value):
            user_msg = (f'Warning. There are more categories (n={len(self.fmt_categories)})'
                        f' than values (n={len(self.value)})')
            self.add_err_msg(user_msg)

            logger.warning(user_msg)
            logger.warning(f'Categories (n={len(self.categories)}): {self.categories}')
            logger.warning(f'Values (n={len(self.value)}): {self.value}')
            return

        self.value = dict(categories=fmt_categories,
                          values=self.value,
                          category_value_pairs=list(zip(fmt_categories, self.value)))

        logger.info((f"Epsilon: {self.epsilon}"
                     f"\nColumn name: {self.variable}"
                     f"\nColumn index: {self.col_index}"
                     f"\nAccuracy value: {self.accuracy_val}"
                     f"\nAccuracy message: {self.accuracy_msg}"
                     f"\n\nDP Histogram: {self.value}"))

        return True