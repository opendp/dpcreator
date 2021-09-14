"""
Convenience Class for a statistic
"""
from abc import ABCMeta, abstractmethod
from django.core.exceptions import ValidationError
from opendp.mod import OpenDPException

from opendp_apps.utils.extra_validators import \
    (validate_confidence_interval,
     validate_float,
     validate_statistic,
     validate_epsilon_not_null,
     validate_not_empty_or_none,
     validate_not_negative,
     validate_int_greater_than_zero)
from opendp_apps.analysis.stat_valid_info import StatValidInfo


class StatSpec:
    __metaclass__ = ABCMeta

    prop_validators = dict(statistic=validate_statistic,
                           dataset_size=validate_int_greater_than_zero,
                           #
                           epsilon=validate_epsilon_not_null,
                           delta=validate_float,  # add something more!
                           ci=validate_confidence_interval,
                           #
                           min=validate_not_negative,
                           max=validate_not_negative,
                           categories=validate_not_empty_or_none,  # ?
                           #
                           impute_constant=validate_not_empty_or_none, # more complex check
                           #
                           accuracy=validate_not_negative)


    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        self.var_name = props.get('var_name')
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

        self.value = None

        self.has_error = False
        self.error_messages = []

        self.run_basic_validation()
        #self.run_additional_validation()



    @abstractmethod
    @property
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
            return True
        except OpenDPException as ex_obj:
            self.add_err_msg(ex_obj.message)
        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(ex_obj.message)
            else:
                self.add_err_msg(str(ex_obj))

        return False

    def run_basic_validations(self):
        """Evaluate the properties, make sure they are populated"""

        # Always validate these properties
        self.validate_property('statistic')
        self.validate_property('epsilon')
        self.validate_property('dataset_size')

        # Add additional required properties.
        #   e.g. min, max, delta, etc.
        for prop_name in self.additional_required_props:
            if prop_name in self.prop_validators:
                self.validate_property(prop_name)

        # check the min/max relationship
        #
        if not self.has_error():
            if 'min' in self.get_additional_required_props and \
                    'max' in self.get_additional_required_props:
                if not self.max > self.min:
                    self.add_err_msg('The "max" must be greater than the "min"')
                    return



    def validate_property(self, prop_name: str, validator=None) -> bool:
        """Validate a property name using a validator"""
        if validator is None:
            validator = self.prop_validators.get('prop_name')

        try:
            validator(getattr(self, prop_name))
        except ValidationError as err_obj:
            user_msg = f'{prop_name}:  {err_obj.message}'
            self.add_err_msg(err_obj.message)
            return False

        return True


    def has_error(self):
        """Did an error occur?"""
        return self.error_found


    def get_error_messages(self):
        """Return the error message if 'has_error' is True"""
        assert self.has_error(), \
            "Please check that '.has_error()' is True before using this method"

        return self.error_messages


    def get_err_msgs(self):
        """Return the error message if 'has_error' is True"""
        return self.get_error_messages()


    def add_err_msg(self, err_msg):
        """Add an error message"""
        self.error_found = True
        self.error_messages.append(err_msg)


    def add_error_message(self, err_msg):
        """Add an error message -- same as "add_err_msg" """
        self.add_err_msg(err_msg)