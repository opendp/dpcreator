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

enable_features("floating-point")

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
                      ci=CI_95.
                      impute_constant=1)
    """

    def additional_required_props(self):
        """
        Add a list of required properties
        example: ['min', 'max']
        """
        return ['min', 'max', 'ci', 'impute_constant']

    def run_initial_handling(self):
        """
        Make sure values are consistently floats
        """
        if self.impute_constant is not None:
            pass

        # Use the "impute_value" for missing values, make sure it's a float!
        #
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            # Convert the impute value to a float!
            if not self.convert_to_float('impute_constant'):
                return

        self.floatify_int_values()

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
        """To implement!"""
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
            # Cast the column as Vec<Optional<Float>>
            make_cast(TIA=str, TOA=float) >>
            # Impute missing values to 0 Vec<Float>
            make_impute_constant(self.impute_constant) >>
            # Clamp age values
            make_clamp(self.get_bounds()) >>
            make_bounded_resize(self.dataset_size, self.get_bounds(), self.impute_constant) >>
            make_sized_bounded_mean(self.dataset_size, self.get_bounds())
        )

        self.scale = binary_search(lambda s: self.check_scale(s, preprocessor, 1, self.epsilon), bounds=(0.0, 1000.0))
        preprocessor = preprocessor >> make_base_laplace(self.scale)

        # keep a point to preprocessor in case it's re-used
        self.preprocessor = preprocessor

        return preprocessor

    def set_accuracy(self):
        """Return the accuracy measure using Laplace and the confidence interval as alpha"""
        if self.has_error():
            return False

        if not self.preprocessor:
            self.preprocessor = self.get_preprocessor()

        self.accuracy_val = laplacian_scale_to_accuracy(self.scale, self.ci)
        self.accuracy_message = f"Releasing {self.statistic} for the variable {self.variable}. " \
                                f"With at least probability {1-self.ci} the output {self.statistic} " \
                                f"will differ from the true mean by at most {self.accuracy_val} units. " \
                                f"Here the units are the same units the variable has in the dataset."

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

        print('column_names', column_names)

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
               f"\nColumn index: {self.accuracy_val}"
               f"\nColumn index: {self.accuracy_message}"
               f"\n\nDP Mean: {self.value}" ))

        return True