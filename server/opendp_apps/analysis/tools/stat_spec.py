"""
BaseClass for Univariate statistics for OpenDP.
    - See "dp_mean_spec.py for an example of instantiation
- Implement the methods marked with "@abstractmethod"
    - Start with additional_required_props
- Instantiation with correct properties for the Statistic will make basic
    checks: is epsilon within a reasonable range, are min/max numbers where min < max, etc.
- Implementing the "get_preprocessor" method acts as validation.
-
"""
from abc import ABCMeta, abstractmethod
from django.core.exceptions import ValidationError
from opendp.mod import OpenDPException

from opendp_apps.model_helpers.basic_err_check import BasicErrCheckList

from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import \
    (validate_confidence_interval,
     validate_float,
     validate_statistic,
     validate_epsilon_not_null,
     validate_not_empty_or_none,
     validate_not_none,
     validate_not_negative,
     validate_int_greater_than_zero,
     validate_int_not_negative)
from opendp_apps.analysis.stat_valid_info import StatValidInfo


class StatSpec(BasicErrCheckList):
    __metaclass__ = ABCMeta

    prop_validators = dict(statistic=validate_statistic,
                           dataset_size=validate_int_greater_than_zero,
                           col_index=validate_int_not_negative,
                           #
                           epsilon=validate_epsilon_not_null,
                           delta=validate_not_negative,  # add something more!
                           ci=validate_confidence_interval,
                           #
                           min=validate_float,
                           max=validate_float,
                           categories=validate_not_empty_or_none,  # ?
                           #
                           #missing_val_handling=
                           #impute_constant=validate_not_none, # more complex check
                           #fixed_value=
                           #
                           accuracy=validate_not_negative)


    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        self.var_name = props.get('var_name')
        self.col_index = props.get('col_index')
        self.statistic = props.get('statistic')
        self.dataset_size = props.get('dataset_size')
        #
        self.epsilon = props.get('epsilon')
        self.delta = props.get('delta')
        self.ci = props.get('ci')
        #
        self.accuracy = props.get('accuracy')
        #
        self.missing_val_handling = props.get('missing_val_handling')
        self.impute_constant = props.get('impute_constant')
        #self.missing_fixed_val = props.get('missing_fixed_val')
        #
        # Note: min, max, categories are sent in via variable_info
        self.variable_info = props.get('variable_info', {}) # derive the min/max if needed
        self.min = self.variable_info.get('min')
        self.max = self.variable_info.get('max')

        self.categories = self.variable_info.get('categories')
        self.var_type = self.variable_info.get('type')

        self.value = None

        self.run_additional_handling()
        self.run_basic_validation()


    @abstractmethod
    def run_additional_handling(self):
        """
        This is a place for additional checking/transformations
        such as making sure values are floats
        Example:
        `self.floatify_int_values()`
        """
        pass

    @abstractmethod
    def additional_required_props(self):
        """
        Add a list of required properties.
        For example, a DP Mean might be:
        `   return ['min', 'max', 'ci']`
        """
        return []


    @abstractmethod
    def check_scale(self, scale, preprocessor, dataset_distance):
        """To implement!"""
        if self.has_error():
            return
        pass
        # return (preprocessor >> make_base_laplace(scale)).check(dataset_distance, self.epsilon)

    @abstractmethod
    def get_preprocessor(self):
        """See "dp_mean_spec.py for an example of instantiation"""
        if self.has_error():
            return
        pass
        # return preprocessor

    @abstractmethod
    def calculate_statistic(self, variabl_names, data):
        """See "dp_mean_spec.py for an example of instantiation"""
        if self.has_error():
            return
        pass


    def get_bounds(self):
        """Return bounds based on the min/max values
        Made into a separate function re: b/c of post init
        transforms such as `floatify_int_values`
        """
        return (self.min, self.max)


    def is_valid(self):
        """Checking validity is accomplished by building the preprocessor"""
        if self.has_error():
            return False

        try:
            self.get_preprocessor()
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

    def floatify_int_values(self, more_props_to_floatify=[]):
        """
        The OpenDP library throws domain mismatches
        if all parameters aren't the same type.
        Example: min = 1, but the data itself is float,
        an error will occurs. This method sets needed
        params to float by adding 0.0
        (ain't too pretty)

        - more_props_to_floatify - list of additional properties to "floatify"
        """
        assert isinstance(more_props_to_floatify, list), \
            '"more_props_to_floatify" must be a list, even and empty list'

        props_to_floatify = ['epsilon', 'ci', 'min', 'max', 'impute_constant', ] \
                            + more_props_to_floatify

        for prop_name in props_to_floatify:
            prop_val = getattr(self, prop_name)
            #
            # if the property is an int, make it a float...
            if isinstance(prop_val, int):
                setattr(self, prop_name, prop_val + 0.0)

    def run_basic_validation(self):
        """Evaluate the properties, make sure they are populated"""

        # Always validate these properties, mostly using the self.prop_validators
        #
        self.validate_property('statistic')
        self.validate_property('epsilon')
        self.validate_property('dataset_size')
        self.validate_property('col_index')
        if not self.var_type in pstatic.VALID_VAR_TYPES:
            self.add_err_msg(f'Invalid variable type: "{self.var_type}"')

        # Add additional required properties.
        #   e.g. min, max, delta, etc.
        for prop_name in self.additional_required_props():
            if prop_name in self.prop_validators:
                self.validate_property(prop_name)

        # check the min/max relationship
        #
        if not self.has_error():
            if 'min' in self.additional_required_props() and \
                    'max' in self.additional_required_props():
                if not self.max > self.min:
                    self.add_err_msg('The "max" must be greater than the "min"')
                    return



    def validate_property(self, prop_name: str, validator=None) -> bool:
        """Validate a property name using a validator"""
        if validator is None:
            validator = self.prop_validators.get(prop_name)
            if validator is None:
                self.add_err_msg(f'Validator not found for property "{prop_name}"')
                return

        # print('prop_name', prop_name)
        try:
            validator(getattr(self, prop_name))
        except ValidationError as err_obj:
            user_msg = f'{prop_name}:  {err_obj.message}'
            self.add_err_msg(user_msg)
            return False

        return True

    def print_debug(self):
        """show params"""
        for key, val in self.__dict__.items():
            print(f'{key}: {val}')