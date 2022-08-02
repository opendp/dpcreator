"""
Wrapper class for DP Mean functionality


"""
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.meas import make_base_laplace
from opendp.mod import binary_search, enable_features
from opendp.trans import \
    (make_bounded_resize,
     make_cast,
     make_clamp,
     make_impute_constant,
     make_select_column,
     make_sized_bounded_mean,
     make_split_dataframe)
from opendp.mod import OpenDPException

enable_features("floating-point", "contrib")

from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis import static_vals as astatic


class DPMeanSpec(StatSpec):
    """
    Initiate with dict of properties. Example of needed properties:

    spec_props = dict(var_name="hours_sleep",
                      col_index=3,
                      variable_info=dict(min=0, max=24, type=VAR_TYPE_FLOAT),
                      statistic=DP_MEAN,
                      dataset_size=365,
                      epsilon=0.5,
                      cl=CL_95,
                      fixed_value=1)
    """
    STATISTIC_TYPE = astatic.DP_MEAN

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        super().__init__(props)
        self.noise_mechanism = astatic.NOISE_LAPLACE_MECHANISM

    def additional_required_props(self):
        """
        Add a list of required properties
        example: ['min', 'max']
        """
        return ['min', 'max', 'cl',]    # 'fixed_value']

    def run_01_initial_handling(self):
        """
        Make sure values are consistently floats
        """
        if not self.statistic == self.STATISTIC_TYPE:
            self.add_err_msg(f'The specified "statistic" is not "{self.STATISTIC_TYPE}". (StatSpec)"')

        if self.fixed_value is not None:
            pass

        # Use the "impute_value" for missing values, make sure it's a float!
        #
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            # Convert the impute value to a float!
            if not self.cast_property_to_float('fixed_value'):
                return
        self.floatify_int_values()

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
            self.add_err_msg('DPMeanSpec.run_chain(..): column_names must be a list. Found: (type({column_names}))')
            return

        try:
            parse_dataframe = make_split_dataframe(separator=sep_char,
                                                   col_names=column_names)

            computation_chain = parse_dataframe >> self.preprocessor
            # if file_extension != '.csv':
            #     file_obj.write('temp.csv')
            # with open('temp.csv') as file_obj:
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

        #print((f"Epsilon: {self.epsilon}"
        #       f"\nColumn name: {self.variable}"
        #       f"\nColumn index: {self.col_index}"
        #       f"\nColumn accuracy_val: {self.accuracy_val}"
        #       f"\nColumn accuracy_message: {self.accuracy_message}"
        #       f"\n\nDP Mean: {self.value}" ))

        return True
