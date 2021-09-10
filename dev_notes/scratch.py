
from opendp.trans import *
from opendp.meas import *
from opendp.core import *
from opendp_apps.model_helpers.basic_err_check import BasicErrCheck

KNOWN_DATA_TYPES = ['Categorical', 'Boolean', 'Float', 'Integer']

class StatisticSpecNumeric(BasicErrCheck):

    required_fields = ['index', 'data_type', 'lower', 'upper', 'n', 'epsilon']

    def __init__(self, index: int, data_type: str, lower, upper, n: int, epsilon):
        """Basic data needed to construct a numeric statistic"""
        self.index = index
        self.data_type = data_type
        self.lower = lower
        self.upper = upper
        self.n = n
        self.epsilon = epsilon

        self.is_valid = False
        self.validate_spec()

    def validate_spec(self):
        """Make sure that the statistic_spec looks okay"""

        # (1) Check that required fields aren't None
        for req_field in self.required_fields:
            if self.__dict__.get(req_field) is None:
                self.add_error_message(f'The field "{req_field}" must be specified')

        if self.has_error():
            return

        if not self.data_type in KNOWN_DATA_TYPES:
            self.add_error_message(f'The data type "{self.data_type}" is unknown')

        if not self.upper > self.lower:
            self.add_error_message('The upper bound must be greater than the lower bound')

        # etc, etc.


class DPMeanLaPlace:

    error_found = False
    error_messages = []
    required_fields = ['col_names', 'index', 'data_type', 'lower', 'upper', 'n', 'epsilon']

    def __init__(self, statistic_spec: StatisticSpecNumeric, col_names: list, index: int, **kwargs):
        """Constructor"""
        self.statistic_spec = statistic_spec
        self.col_names = col_names

        self.data_source = self.kwargs.get('data_source')



    def is_valid(self):
        """Construct"""
        if self.has_error():
            return False

        preprocessor = self.construct_preprocessor()
        if preprocessor is None:
            return False

        return True


    def construct_preprocessor(self):
        """build the preprocessor, e.g. as in the example
        https://github.com/opendp/opendp/blob/main/python/example/private_mean.ipynb"""
        if self.has_error():
            return None

        try:
            bounds = (lower, upper)
            preprocessor = (
                # Convert data into Vec<Vec<String>>
                    make_split_dataframe(separator=",", col_names=col_names) >>
                    # Selects a column of df, Vec<str>
                    make_select_column(key=index, TOA=str) >>
                    # Cast the column as Vec<Optional<Float>>
                    make_cast(TIA=str, TOA=float) >>
                    # Impute missing values to 0 Vec<Float>
                    make_impute_constant(0.) >>
                    # Clamp age values
                    make_clamp(bounds) >>
                    #make_bounded_resize(0., n, lower, upper) >>
                    make_bounded_resize(n, bounds, 0.) >>

                    make_sized_bounded_mean(n, bounds)

                    #make_bounded_mean(lower, upper, n=n, T=float)
            )
            scale = binary_search(lambda s: check_scale(s, preprocessor, 1, epsilon), (0., 10.))
            preprocessor = preprocessor >> make_base_laplace(scale)
        except SomeDPError as err_obj:
            self.add_err_msg('usable error message')
            return None
        except SomeOtherDPError as err_obj:
            self.add_err_msg('usable error message')
            return None

        return preprocessor


    def has_error(self):
        """Did an error occur?"""
        return self.error_found

    def get_error_message(self):
        """Return the error message if 'has_error' is True"""
        assert self.has_error(),\
            "Please check that '.has_error()' is True before using this method"

        return self.error_message

    def add_error_message(self, err_msg):
        """Add an error message"""
        self.error_found = True
        self.error_messages.append(err_msg)
