"""
Convenience Class for a statistic
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
                           impute_constant=validate_not_none, # more complex check
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
        self.impute_constant = props.get('impute_constant')
        #
        # Note: min, max, categories are sent in via variable_info
        self.variable_info = props.get('variable_info', {}) # derive the min/max if needed
        self.min = self.variable_info.get('min')
        self.max = self.variable_info.get('max')
        self.bounds = (self.min, self.max)
        self.categories = self.variable_info.get('categories')
        self.var_type = self.variable_info.get('type')

        self.value = None

        self.run_basic_validation()
        #self.run_additional_validation()



    @abstractmethod
    def additional_required_props(self):
        """
        Add a list of required properties
        example: ['min', 'max']
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
        """To implement!"""
        if self.has_error():
            return
        pass
        # return preprocessor

    def is_valid(self):
        """Checking validity is building the preprocessor"""
        if self.has_error():
            return False

        try:
            self.get_preprocessor()
        except OpenDPException as ex_obj:
            self.add_err_msg(ex_obj.message)
            return False

        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(ex_obj.message)
            else:
                self.add_err_msg(str(ex_obj))
            return False

        return True

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

