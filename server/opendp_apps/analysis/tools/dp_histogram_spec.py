from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.trans import *
from opendp.meas import *
from opendp.mod import enable_features, binary_search_param, OpenDPException
from opendp.typing import *

from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler.static_vals import VAR_TYPE_INTEGER, VAR_TYPE_CATEGORICAL

enable_features("floating-point", "contrib")


class DPHistogramSpec(StatSpec):
    """

    """
    STATISTIC_TYPE = astatic.DP_HISTOGRAM

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)

    def additional_required_props(self):
        """
        Add a list of required properties
        example: ['min', 'max']
        """
        return ['min', 'max']

    def run_01_initial_handling(self):
        """
        """
        if not self.statistic == self.STATISTIC_TYPE:
            self.add_err_msg(f'The specified "statistic" is not "{self.STATISTIC_TYPE}". (StatSpec)"')
            return

        if self.var_type == VAR_TYPE_INTEGER:
            self.categories = [int(i) for i in range(self.min, self.max)]
            self.fixed_value = int(self.fixed_value)
            # print(self.categories, self.fixed_value)

        # Using integers
        #
        if self.var_type == VAR_TYPE_INTEGER:
            if self.fixed_value is not None:
                if not self.cast_property_to_int('fixed_value'):
                    return

        # if self.var_type == VAR_TYPE_CATEGORICAL:

        # TODO: These default values are allowing the tests to pass,
        #  but we need to process cases where min and max are referring to counts of a
        #  categorical variable.
        if not self.min:
            self.min = 0
        elif self.cast_property_to_int('min') is False:
            return

        if not self.max:
            self.max = 10
        elif self.cast_property_to_int('max') is False:
            return

    def run_03_custom_validation(self):
        """
        This is a place for initial checking/transformations
        such as making sure values are floats
        Example:
        self.check_numeric_fixed_value()
        """
        if self.has_error():
            return

        if self.var_type == VAR_TYPE_INTEGER:
            self.check_numeric_fixed_value()

    def check_scale(self, scale, preprocessor):
        """
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

        # Have we already already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        # TODO: More general type handling
        if self.var_type == VAR_TYPE_INTEGER:
            toa = int
            tia = int
        else:
            toa = str
            tia = str

        preprocessor = (
            make_select_column(key=self.col_index, TOA=str) >>
            make_cast(TIA=str, TOA=toa) >>
            make_impute_constant(self.fixed_value) >>
            make_count_by_categories(categories=self.categories, MO=L1Distance[int], TIA=tia)
        )

        self.scale = binary_search_param(
            lambda s: self.check_scale(s, preprocessor), d_in=1, d_out=self.epsilon)
        preprocessor = preprocessor >> make_base_geometric(scale=self.scale, D=VectorDomain[AllDomain[int]])

        # keep a pointer to the preprocessor in case it's re-used
        self.preprocessor = preprocessor
        return preprocessor

    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence level alpha"""
        if self.has_error():
            return False

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        # This is for histograms, so divide alpha by the number of counts
        cl_alpha = self.get_confidence_level_alpha() / len(self.categories)
        if cl_alpha is None:
            # Error already saved
            return False
        self.accuracy_val = laplacian_scale_to_accuracy(self.scale, cl_alpha)

        # Note `self.accuracy_val` must bet set before using `self.get_accuracy_text()
        self.accuracy_msg = self.get_accuracy_text(template_name='analysis/dp_histogram_accuracy_default.html')

        return True

    def run_chain(self, column_names, file_obj, sep_char=","):
        """
        Calculate the stats! See "dp_mean_spec.py" for an example of instantiation

        :param columns, Example: [0, 1, 2, 3] or ['a', 'b', 'c', 'd'] -- depends on your stat!
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
            self.add_err_msg('DPHistogramSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
            return

        try:
            parse_dataframe = make_split_dataframe(separator=sep_char,
                                                   col_names=column_names)

            computation_chain = parse_dataframe >> self.preprocessor

            self.value = computation_chain(file_obj.read())

        except OpenDPException as ex_obj:
            print(ex_obj)
            self.add_err_msg(f'{ex_obj.message} (OpenDPException)')
            return False
        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        print((f"Epsilon: {self.epsilon}"
               f"\nColumn name: {self.variable}"
               f"\nColumn index: {self.col_index}"
               f"\nAccuracy value: {self.accuracy_val}"
               f"\nAccuracy message: {self.accuracy_msg}"
               f"\n\nDP Histogram (n={len(self.value)}): {self.value}" ))

        if self.var_type == VAR_TYPE_CATEGORICAL:
            print(f"Categories (n={len(self.categories)}): {self.categories}")
        elif self.var_type == VAR_TYPE_INTEGER:
            int_cats = [x for x in range(self.min, self.max)] + [self.max]
            print(f"Categories (integers) (n={len(int_cats)}): {int_cats}")


        return True