from opendp.trans import *
from opendp.meas import *
from opendp.mod import enable_features, binary_search_param, OpenDPException
from opendp.typing import *

from opendp_apps.analysis.tools.stat_spec import StatSpec

enable_features("contrib")
enable_features("floating-point")


class DPHistogramSpec(StatSpec):
    """
    Initiate with dict of properties. Example of needed properties:

    spec_props = dict(var_name="hours_sleep",
                      col_index=3,
                      variable_info=dict(min=0, max=24, type=VAR_TYPE_FLOAT),
                      statistic=DP_HISTOGRAM,
                      dataset_size=365,
                      epsilon=0.5,
                      ci=CI_95.
                      fixed_value=1)
    """
    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        # TODO: Generates an error when this isn't initialized somewhere
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
        if self.fixed_value is not None:
            # attempt conversion to int
            if not self.convert_to_int('fixed_value'):
                return

        # TODO: These default values are allowing the tests to pass,
        #  but we need to process cases where min and max are referring to counts of a
        #  categorical variable.
        if not self.min:
            self.min =  0.0
        elif self.convert_to_int('min') is False:
            return

        if not self.max:
            self.max = 10.0
        elif self.convert_to_int('max') is False:
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

        preprocessor = (
            make_select_column(key=self.col_index, TOA=str) >>
            make_count_by_categories(categories=self.categories, MO=L1Distance[int], TIA=str)
        )

        self.scale = binary_search_param(
            lambda s: self.check_scale(s, preprocessor), d_in=1, d_out=self.epsilon)
        preprocessor = preprocessor >> make_base_geometric(scale=self.scale, D=VectorDomain[AllDomain[int]])

        # keep a pointer to the preprocessor in case it's re-used
        self.preprocessor = preprocessor
        return preprocessor


    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence interval as alpha"""
        if self.has_error():
            return False

        self.accuracy_val = None  # Future: self.geometric_scale_to_accuracy()
        self.accuracy_msg = None

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
               f"\n\nDP Histogram: {self.value}" ))

        return True