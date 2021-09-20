from opendp.trans import *
from opendp.meas import *
from opendp.core import *
from opendp.typing import *

enable_features("floating-point")

from opendp_apps.analysis.tools.stat_spec import StatSpec


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
        self.accuracy_msg = ""
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
            self.fixed_value = int(self.fixed_value)
        # TODO: These default values are allowing the tests to pass,
        #  but we need to process cases where min and max are referring to counts of a
        #  categorical variable.
        self.min = int(self.min) if self.min else 0.0
        self.max = int(self.max) if self.max else 10.0

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
        """
        Set up and return computation chain
        :return:
        """

        if self.has_error():
            return

        # Have we already already assembled it?
        #
        if self.preprocessor is not None:
            # Yes!
            return self.preprocessor

        try:
            preprocessor = (
                # Convert data into Vec<Vec<String>>
                    # Selects a column of df, Vec<str>
                    make_select_column(key=self.col_index, TOA=str) >>
                    # Cast the column as Vec<Int>
                    # make_cast(TIA=str, TOA=str) >>
                    # Impute missing values to 0
                    # make_impute_constant(self.fixed_value) >>
                    make_count_by_categories(categories=self.categories, MO=L1Distance[float])
                # make_base_geometric(scale=1., bounds=(0,201), D="VectorDomain<AllDomain<i32>>")
            )

            # self.scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon), bounds=(0, 1000))

            # preprocessor = preprocessor >> make_base_geometric(scale=1., D=VectorDomain[AllDomain[int]])

            # keep a point to preprocessor in case it's re-used
            self.preprocessor = preprocessor
            return preprocessor

        except Exception as ex:
            self.add_err_msg(ex)


    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence interval as alpha"""
        if self.has_error():
            return False

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        self.accuracy_val = None
        self.accuracy_message = ""

        return True

    def run_chain(self, column_names, file_obj, sep_char=","):
        """
        Calculate the stats! See "dp_mean_spec.py" for an example of instantiation

        :param columns. Examples: [0, 1, 2, 3] or ['a', 'b', 'c', 'd'] -- depends on your stat!
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
               f"\nAccuracy message: {self.accuracy_message}"
               f"\n\nDP Histogram: {self.value}" ))

        return True