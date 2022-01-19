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
import abc # import ABC, ABCMeta, abstractmethod
from collections import OrderedDict
import decimal

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string


from opendp.mod import OpenDPException

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.profiler.static_vals import VAR_TYPE_INTEGER
from opendp_apps.utils.extra_validators import \
    (validate_confidence_level,
     validate_float,
     validate_statistic,
     validate_epsilon_not_null,
     validate_missing_val_handlers,
     validate_not_empty_or_none,
     validate_not_negative,
     validate_int_greater_than_zero,
     validate_int_not_negative)
from opendp_apps.analysis.stat_valid_info import StatValidInfo


class StatSpec:
    __metaclass__ = abc.ABCMeta

    prop_validators = dict(statistic=validate_statistic,
                           dataset_size=validate_int_greater_than_zero,
                           col_index=validate_int_not_negative,
                           #
                           epsilon=validate_epsilon_not_null,
                           delta=validate_not_negative,  # add something more!
                           cl=validate_confidence_level,
                           #
                           min=validate_float,
                           max=validate_float,
                           categories=validate_not_empty_or_none,  # ?
                           #
                           missing_values_handling=validate_missing_val_handlers,
                           # fixed_value=validate_not_none, # more complex check
                           # fixed_value=
                           #
                           accuracy=validate_not_negative)

    def __init__(self, props: dict):
        """Set the internals using the props dict"""
        # print('stat_spec.initial props', props)
        self.variable = props.get('variable')
        self.col_index = props.get('col_index')
        self.statistic = props.get('statistic')
        self.dataset_size = props.get('dataset_size')
        #
        self.epsilon = props.get('epsilon')
        self.delta = props.get('delta')

        self.cl = props.get('cl')      # confidence level coefficient (e.g. .95, .99, etc)

        #
        self.accuracy_val = None
        self.accuracy_msg = None
        #
        self.missing_values_handling = props.get('missing_values_handling')
        self.fixed_value = props.get('fixed_value')
        # self.missing_fixed_val = props.get('missing_fixed_val')
        #
        # Note: min, max, categories are sent in via variable_info
        self.variable_info = props.get('variable_info', {})  # derive the min/max if needed
        self.min = self.variable_info.get('min')
        self.max = self.variable_info.get('max')

        self.categories = self.variable_info.get('categories')
        self.var_type = self.variable_info.get('type')
        # print("VAR TYPE", self.var_type)
        if self.var_type == VAR_TYPE_INTEGER:
            self.categories = [int(i) for i in range(self.min, self.max)]
            self.fixed_value = int(self.fixed_value)
            # print(self.categories, self.fixed_value)
        self.preprocessor = None  # set this each time get_preprocessor is called--hopefully once
        self.value = None
        self.scale = None

        # error handling
        self.error_found = False
        self.error_messages = []

        self.run_01_initial_handling()  # customize, if types need converting, etc.
        self.run_02_basic_validation()  # always the same
        self.run_03_custom_validation()  # customize, if types need converting, etc.

    def get_cl_text(self):
        """Return the ci as text. e.g. .05 is returned as 95%"""
        if not self.cl:
            return None

        cl_fmt = self.cl * 100

        return f'{cl_fmt}%'

    @abc.abstractmethod
    def additional_required_props(self):
        """
        Add a list of required properties.
        For example, a DP Mean might be:
        `   return ['min', 'max', 'cl']`
        """
        raise NotImplementedError('additional_required_props')

    @abc.abstractmethod
    def run_01_initial_handling(self):
        """
        This is a place for initial checking/transformations
        such as making sure values are floats
        Example:
        `self.floatify_int_values()`

        See "dp_mean_spec.py for an example of instantiation

        Always start implementation with:
        ```
        if self.has_error():
            return

        """
        raise NotImplementedError('run_01_initial_handling')

    @abc.abstractmethod
    def run_03_custom_validation(self):
        """
        This is a place for custom checking/transformations
        such as making sure values are floats

        See "dp_mean_spec.py for an example of instantiation

        Always start implementation with:
        ```
        if self.has_error():
            return False
        ```

        Or, if not implemented, simply use
        ```
        pass
        ```
        """
        raise NotImplementedError('run_03_custom_validation')

    @abc.abstractmethod
    def check_scale(self, scale, preprocessor):
        """
        See "dp_mean_spec.py for an example of instantiation

        Always start implementation with:
        ```
        if self.has_error():
            return False
        ```

        Or, if not implemented, simply use
        ```
        pass
        ```
        """
        raise NotImplementedError('check_scale')

    @abc.abstractmethod
    def get_preprocessor(self):
        """
        See "dp_mean_spec.py for an example of instantiation

        Always start implementation with:
        ```
        if self.has_error():
            return False
        ```

        These should be the last two lines of the method
        ```
        self.preprocessor = preprocessor
        return preprocessor
        ```
        """
        raise NotImplementedError('get_preprocessor')

    @abc.abstractmethod
    def run_chain(self, columns: list, file_obj, sep_char=","):
        """
        Calculate the stats! See "dp_mean_spec.py" for an example of instantiation

        :param columns - for example [0, 1, 2, 3] or ['a', 'b', 'c', 'd'] -- depends on your stat!
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

        Always start implementation with:
        ```
        if self.has_error():
            return False
        ```
        """
        raise NotImplementedError('run_chain')

    @abc.abstractmethod
    def set_accuracy(self):
        """
        See "dp_mean_spec.py for an example of instantiation

        Always start implementation with:
        ```
        if self.has_error():
            return False
        ```

        Or, if not implemented, simply use
        ```
        pass
        ```
        """
        raise NotImplementedError()

    def get_bounds(self):
        """Return bounds based on the min/max values
        Made into a separate function re: b/c of post init
        transforms such as `floatify_int_values`
        """
        return (self.min, self.max)

    def is_chain_valid(self):
        """Checking validity is accomplished by building the preprocessor"""
        if self.has_error():
            return False

        try:
            self.get_preprocessor()
            self.set_accuracy()
        except OpenDPException as ex_obj:
            self.add_err_msg(f'{ex_obj.message} (OpenDPException)')
            return False

        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        # Important, even if an exception wasn't thrown, an error may have been found
        if self.has_error():
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

        props_to_floatify = ['epsilon', 'cl', 'min', 'max',] \
                            + more_props_to_floatify

        for prop_name in props_to_floatify:
            if not self.convert_to_float(prop_name):
                return

    def run_02_basic_validation(self):
        """Evaluate the properties, make sure they are populated"""
        if self.has_error():  # something may be wrong in "run_01_initial_handling()"
            return

        # Always validate these properties, mostly using the self.prop_validators
        #
        self.validate_property('statistic')
        self.validate_property('epsilon')
        self.validate_property('dataset_size')
        self.validate_property('col_index')
        self.validate_property('missing_values_handling')

        if not self.var_type in pstatic.VALID_VAR_TYPES:
            self.add_err_msg(f'Invalid variable type: "{self.var_type}"')
            return

        # Add additional required properties.
        #   e.g. min, max, delta, etc.
        for prop_name in self.additional_required_props():
            if prop_name in self.prop_validators:
                self.validate_property(prop_name)

        # check the min/max relationship
        #
        if self.has_error():
            return
        if 'min' in self.additional_required_props() and \
                'max' in self.additional_required_props():
            # print('checking min/max!')
            # print('min', self.min, type(self.min))
            # print('max', self.max, type(self.max))
            if self.max > self.min:
                pass
            else:
                user_msg = f'{self.variable} The min ({self.min}) must be less than the max ({self.max})'
                self.add_err_msg(user_msg)
                # self.add_err_msg(astatic.ERR_MSG_INVALID_MIN_MAX)
                return
            # print('looks okay!')

        # If this is numeric variable, check the impute constant
        #   (If impute constant isn't used, this check will simply exit)
        # if self.var_type in pstatic.NUMERIC_VAR_TYPES:
        #    self.check_numeric_fixed_value()

    def check_numeric_fixed_value(self):
        """
        For the case of handling missing values with a constant
        Check that the fixed value/fixed_value is not outside the min/max range
        """
        if self.has_error():
            return

        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            if self.fixed_value < self.min:
                user_msg = (f'The "fixed value" ({self.fixed_value})'
                            f' {astatic.ERR_IMPUTE_PHRASE_MIN} ({self.min})')
                self.add_err_msg(user_msg)
                return
            elif self.fixed_value > self.max:
                user_msg = (f'The "fixed value" ({self.fixed_value})'
                            f' {astatic.ERR_IMPUTE_PHRASE_MAX} ({self.max})')
                self.add_err_msg(user_msg)
                return

    def validate_property(self, prop_name: str, validator=None) -> bool:
        """Validate a property name using a validator"""
        if self.has_error():
            return

        if validator is None:
            validator = self.prop_validators.get(prop_name)
            if validator is None:
                self.add_err_msg(f'Validator not found for property "{prop_name}"')
                return

        # print('prop_name', prop_name)
        try:
            validator(getattr(self, prop_name))
        except ValidationError as err_obj:
            user_msg = f'{err_obj.message} ({prop_name})'
            self.add_err_msg(user_msg)
            return False

        return True

    def convert_to_float(self, prop_name):
        """Attempt to convert a value to a float"""
        prop_val = getattr(self, prop_name)

        try:
            prop_val_float = float(prop_val)
        except TypeError:
            self.add_err_msg(f'Failed to convert "{prop_name}" to a float. (value: "{prop_val}")')
            return False
        except ValueError:
            self.add_err_msg(f'Failed to convert "{prop_name}" to a float. (value: "{prop_val}")')
            return False

        setattr(self, prop_name, prop_val_float)

        return True

    def convert_to_int(self, prop_name):
        """Attempt to convert a value to an integer"""
        prop_val = getattr(self, prop_name)

        try:
            prop_val_float = int(prop_val)
        except TypeError:
            self.add_err_msg(f'Failed to convert "{prop_name}" to an integer. (value: "{prop_val}")')
            return False
        except ValueError:
            self.add_err_msg(f'Failed to convert "{prop_name}" to a integer. (value: "{prop_val}")')
            return False

        setattr(self, prop_name, prop_val_float)

        return True

    def get_success_msg_dict(self):
        """Get success info"""
        assert self.has_error() is False, \
            "Make sure .has_error() is False before calling this method"

        # Need to add accuracy...
        return StatValidInfo.get_success_msg_dict(self.variable, self.statistic,
                                                  accuracy_val=self.accuracy_val,
                                                  accuracy_msg=self.accuracy_msg)

    def get_error_msg_dict(self):
        """Get invalid info dict"""
        return StatValidInfo.get_error_msg_dict(self.variable,
                                                self.statistic,
                                                self.get_single_err_msg())

    def get_single_err_msg(self):
        """Get the first message in the self.error_messages list"""
        if self.has_error():
            return self.get_err_msgs()[0]
        return None

    def print_debug(self):
        """show params"""
        print('-' * 40)
        import json
        print(json.dumps(self.__dict__, indent=4))
        # for key, val in self.__dict__.items():
        #    print(f'{key}: {val}')

    def get_short_description_text(self):
        """Get description in plain text"""
        template_name = 'analysis/dp_stat_general_description.txt'
        return self.get_short_description_html(template_name)

    def get_short_description_html(self, template_name=None):
        """
        Create an HTML description using a ReleaseInfo object
        """
        info_dict = {
            'stat': self,
            'use_min_max': 'min' in self.additional_required_props(),
            'MISSING_VAL_INSERT_FIXED': astatic.MISSING_VAL_INSERT_FIXED,
            'MISSING_VAL_INSERT_RANDOM': astatic.MISSING_VAL_INSERT_RANDOM
        }

        if not template_name:
            template_name = 'analysis/dp_stat_general_description.html'
            # template_name = 'analysis/dp_stat_general_description_tbl.html'

        desc = render_to_string(template_name, info_dict)

        # print(desc)
        return desc


    def get_accuracy_text(self, template_name=None):
        """
        Create an HTML description using a ReleaseInfo object
        """
        info_dict = {
            'stat': self,
        }

        if not template_name:
            template_name = 'analysis/dp_stat_accuracy_default.txt'

        desc = render_to_string(template_name, info_dict)

        # print(desc)
        return desc

    def get_release_dict(self) -> OrderedDict:
        """Final release info"""
        assert not self.has_error(), \
            'Do not call this method before checking that ".has_error()" is False'
        assert self.value, \
            'Only use this after "run_chain()" was completed successfully"'

        final_info = OrderedDict({
                         "statistic": self.statistic,
                         "variable": self.variable,
                         "result": {
                            "value": self.value
                         },
                         "epsilon": self.epsilon,
                         "delta": self.delta,
                    })

        # Min/Max
        #
        if 'min' in self.additional_required_props():
            final_info['bounds'] = OrderedDict({'min': self.min, 'max': self.max})

        # Categories
        #
        if 'categories' in self.additional_required_props():
            final_info['categories'] = self.categories

        # Missing values
        #
        final_info['missing_value_handling'] = OrderedDict({"type": self.missing_values_handling})
        if self.missing_values_handling == astatic.MISSING_VAL_INSERT_FIXED:
            final_info['missing_value_handling']['fixed_value'] = self.fixed_value

        # Add accuracy
        #
        if self.accuracy_val or self.accuracy_msg:
            final_info['confidence_level'] = self.cl
            final_info['confidence_level_alpha'] = self.get_confidence_level_alpha()
            final_info['accuracy'] = OrderedDict()
            if self.accuracy_val:
                final_info['accuracy']['value'] = self.accuracy_val
            if self.accuracy_msg:
                final_info['accuracy']['message'] = self.accuracy_msg

        final_info['description'] = OrderedDict()
        final_info['description']['html'] = self.get_short_description_html()
        final_info['description']['text'] = self.get_short_description_text()

        return final_info

    def get_confidence_level_alpha(self) -> float:
        """Get the confidence level (CL) alpha. e.g. if CL coefficient is .99, return .01
        Assumes that `self.cl` has passed through the validator: `validate_confidence_level`
        """
        if not self.cl:
            user_msg = f'{astatic.ERR_MSG_CL_ALPHA_CL_NOT_SET} ("{self.cl}")'
            self.add_err_msg(user_msg)
            return None

        try:
            dec_alpha = decimal.Decimal(1 - self.cl).quantize(decimal.Decimal('.01'),
                                                              rounding=decimal.ROUND_DOWN)
        except TypeError as ex_obj:
            user_msg = f'{astatic.ERR_MSG_CL_ALPHA_CL_NOT_NUMERIC} "{self.cl}" ({ex_obj})'
            self.add_err_msg(user_msg)
            return None

        if dec_alpha > 1:
            user_msg = f'{astatic.ERR_MSG_CL_ALPHA_CL_GREATER_THAN_1} ("{dec_alpha}")'
            self.add_err_msg(user_msg)
            return None

        if dec_alpha < 0:
            user_msg = f'{astatic.ERR_MSG_CL_ALPHA_CL_LESS_THAN_0} ("{dec_alpha}")'
            self.add_err_msg(user_msg)
            return None

        return float(dec_alpha)

    def has_error(self) -> bool:
        """Did an error occur?"""
        return self.error_found

    def get_error_messages(self) -> list:
        """Return the error message if 'has_error' is True"""
        assert self.has_error(), \
            "Please check that '.has_error()' is True before using this method"

        return self.error_messages

    def get_err_msgs(self) -> list:
        """Return the error message if 'has_error' is True"""
        return self.get_error_messages()

    def get_err_msgs_concat(self, sep_char=' ') -> str:
        return f'{sep_char}'.join(self.get_error_messages())

    def get_error_messages_concat(self, sep_char=' ') -> str:
        return self.get_err_msgs_concat(sep_char)

    def add_err_msg(self, err_msg: str):
        """Add an error message"""
        # print('add_err_msg. type', type(err_msg))

        self.error_found = True
        self.error_messages.append(err_msg)

    def add_error_message(self, err_msg: str):
        """Add an error message -- same as "add_err_msg" """
        self.add_err_msg(err_msg)
