"""
Reference: https://docs.google.com/spreadsheets/d/1pc0DA-BtbsAag22T3aSXS9MqbXaMVXmaVWfdD56Tj1U/edit#gid=1435268092
BaseClass for Univariate statistics for OpenDP.
    - See "dp_mean_spec.py for an example of instantiation
- Implement the methods marked with "@abstractmethod"
    - Start with additional_required_props
- Instantiation with correct properties for the Statistic will make basic
    checks: is epsilon within a reasonable range, are min/max numbers where min < max, etc.
- Implementing the "get_preprocessor" method acts as validation.
-
"""
import abc
import decimal
import json
from collections import OrderedDict
from typing import Any
from typing import Union

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import render_to_string
from opendp.mod import OpenDPException

from opendp_apps.analysis import static_vals as astatic
from opendp_apps.analysis.stat_valid_info import StatValidInfo
from opendp_apps.profiler import static_vals as pstatic
from opendp_apps.utils.extra_validators import \
    (validate_confidence_level,
     validate_statistic,
     validate_epsilon_not_null,
     validate_not_empty_or_none,
     validate_int_not_negative,
     validate_fixed_value_in_categories,
     # validate_bool_true_false,
     )


class StatSpec:
    __metaclass__ = abc.ABCMeta

    STATISTIC_TYPE = None

    default_validators = dict(statistic=validate_statistic,
                              col_index=validate_int_not_negative,
                              # dataset_size=validate_int_greater_than_zero,
                              epsilon=validate_epsilon_not_null,
                              cl=validate_confidence_level)

    def __init__(self, props: dict):
        """
        The basic constructor reads in a dict of variables and runs basic validation
        @param props:
        """
        # (1) Mandatory fields
        #
        self.statistic = props.get('statistic')  # type of statistic, example: analysis.static_vals.DP_MEAN
        self.variable = props.get('variable')  # variable name
        self.col_index = props.get('col_index')  # column index in the orig dataset
        self.epsilon = float(props.get('epsilon')) if props.get('epsilon') else None
        self.cl = props.get('cl')  # confidence level coefficient (e.g. .95, .99, etc)


        # (1a) histogram specific
        self.histogram_bin_type = props.get('histogram_bin_type')
        self.histogram_number_of_bins = props.get('histogram_number_of_bins')
        self.histogram_bin_edges = props.get('histogram_bin_edges')

        # (2) Retrieved from variable_info - data from the Confirm Variables page
        self.variable_info = props.get('variable_info', {})  # retrieve min/max or categories, if needed
        self.var_type = self.variable_info.get('type')  # mandatory
        self.min = self.variable_info.get('min')  # optional: depends on variable type/stat
        self.max = self.variable_info.get('max')  # optional: depends on variable type/stat
        self.categories = self.variable_info.get('categories')  # optional: depends on variable type/stat
        # optional: for variable type boolean
        self.true_value = self.variable_info.get('trueValue')
        self.false_value = self.variable_info.get('falseValue')

        # (3) Usage depends on the statistic
        #
        self.dataset_size = props.get('dataset_size')  # dataset size
        self.delta = float(props.get('delta')) if props.get('delta') else None  # privacy parameter
        # Missing values handling
        self.missing_values_handling = props.get('missing_values_handling')
        self.fixed_value = props.get('fixed_value')

        # (4) Set explicitly by subclass (may change in the future)
        self.noise_mechanism = None

        # (5) Implementation depends on the statistics; Used for validation and computation
        self.preprocessor = None  # set this each time get_preprocessor is called--hopefully once
        self.prop_validators = {}  # combination of default_validators + get_stat_specific_validators()

        # (6) Output fields
        #
        self.value = None  # DP Stat(s)
        self.scale = None  # Scale

        self.accuracy_val = None  # Accuracy value
        self.accuracy_msg = None  # Accuracy message for user

        # error handling
        self.error_found = False
        self.error_messages = []

        self.run_01_initial_transforms()  # customize, if types need converting, etc.
        self.run_02_basic_validation()  # always the same
        self.run_03_custom_validation()  # customize, if types need converting, etc.

    def get_cl_text(self):
        """Return the ci as text. e.g. .05 is returned as 95%"""
        if not self.cl:
            return None

        cl_fmt = self.cl * 100

        return f'{cl_fmt}%'

    @abc.abstractmethod
    def get_stat_specific_validators(self) -> dict:
        """
        Update self.prop_validators to include validators specific to the subclass
        @return:
        """
        raise NotImplementedError('set_stat_specific_validators')

        # Example: implementation
        """
        return dict(dataset_size=validate_int_greater_than_zero,
                    min=validate_float,
                    max=validate_float,
                    missing_values_handling=validate_missing_val_handlers)
                    
        # OR, if no additional validators
        
        return {} 
        """

    @abc.abstractmethod
    def run_01_initial_transforms(self):
        """
        This is a place for initial transformations such as making sure values are floats
        Example:
        `self.floatify_int_values()`

        See "dp_mean_spec.py for an example of instantiation

        Always start implementation with:
        ```
        if self.has_error():
            return
        ```
        """
        raise NotImplementedError('run_01_initial_transforms')

    @abc.abstractmethod
    def run_03_custom_validation(self):
        """
        This is a place for custom checking/transformations such as making sure min/max values are valid
        Notes:
        - See "dp_mean_spec.py for an example of instantiation
        - Always start implementation with:
            ```
            if self.has_error():
                return False
            ```
        - Or, if not implemented, simply use
            ```
            pass
            ```
        """
        raise NotImplementedError('run_03_custom_validation')

    # TODO: child classes sometimes have 2 params, sometimes have 4
    @abc.abstractmethod
    def check_scale(self, scale, preprocessor, dataset_distance, epsilon):
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
        :param scale:
        :param preprocessor:
        :param dataset_distance:
        :param epsilon:
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
        return self.min, self.max

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
        except AssertionError as err:
            # An AssertionError can be raised from the binary_search method in the OpenDP library for several reasons:
            # 1. Bounds are not the same type
            # 2. Bounds are neither floats nor ints
            # 3. The search value is outside the bounds (assert max != min) which means that we won't find the value we
            #    are looking for.
            # Scenarios 1 and 2 elsewhere and are unlikely to be raised, but scenario 3 can happen when the user's
            # clipping bounds are too broad, so we need to pass back a useful error message to them explaining what
            # they need to do.
            if 'decision boundary' in str(err):
                self.add_err_msg(f'Sorry! The difference between the min and max values for the variable'
                                 f' "{self.variable}" is too large. (This error will be fixed in version 0.5.0 of the'
                                 f' OpenDP library.)')
            else:
                self.add_err_msg(f'Unexpected assertion error when validating the variance statistic.'
                                 f' Exception: {err}')
        except Exception as ex_obj:
            if hasattr(ex_obj, 'message'):
                self.add_err_msg(f'{ex_obj.message} (Exception)')
            else:
                self.add_err_msg(f'{ex_obj} (Exception)')
            return False

        # Important, even if an exception wasn't thrown,
        # an error may have been found earlier
        if self.has_error():
            return False

        return True

    def floatify_int_values(self, props_to_floatify: list = ['cl', 'min', 'max']) -> bool:
        """
        The OpenDP library throws domain mismatches
        if all parameters aren't the same type.
        Example: min = 1, but the data itself is float,
        an error will occurs. This method sets needed
        params to float by adding 0.0
        (ain't too pretty)

        - more_props_to_floatify - list of additional properties to "floatify"
        """
        assert isinstance(props_to_floatify, list), \
            '"props_to_floatify" must be a list. Example: ["epsilon", "cl", "min", "max"]'

        for prop_name in props_to_floatify:
            if self.cast_property_to_float(prop_name) is False:
                return False
        return True

    def get_prop_validator_keys(self):
        """
        Return the keys() of the prop_validators
        @return:
        """
        return list(self.get_prop_validators().keys())

    def get_prop_validators(self) -> dict:
        """
        Return the default validators combined with any subclass specific validators
        @return:
        """
        if not self.prop_validators:
            prop_validators = {}
            prop_validators.update(self.default_validators)
            prop_validators.update(self.get_stat_specific_validators())
            self.prop_validators = prop_validators

        return self.prop_validators

    def run_02_basic_validation(self):
        """This method should be unchanged in subclasses"""
        if self.has_error():  # something may be wrong in "run_01_initial_transforms()"
            return

        if not self.statistic == self.STATISTIC_TYPE:
            self.add_err_msg(f'The specified "statistic" is not "{self.STATISTIC_TYPE}".')
            return

        # Epsilon should always be a float
        if not self.cast_property_to_float('epsilon'):
            return

        # Delta, if specified, should be a float
        if self.delta is not None:
            if not self.cast_property_to_float('delta'):
                return

        # Check the var_type
        if self.var_type not in pstatic.VALID_VAR_TYPES:
            self.add_err_msg(f'Invalid variable type: "{self.var_type}"')
            return

        # Run the validators
        for attr_name in self.get_prop_validator_keys():
            if not self.validate_property(attr_name):
                return

    def validate_property(self, prop_name: str, validator=None) -> bool:
        """Validate a property name using a validator"""
        if self.has_error():
            return False

        if validator is None:
            validator = self.get_prop_validators().get(prop_name)
            if validator is None:
                self.add_err_msg(f'Validator not found for property "{prop_name}"')
                return False

        try:
            validator(getattr(self, prop_name))
        except ValidationError as err_obj:
            user_msg = f'{err_obj.message} ({prop_name})'
            self.add_err_msg(user_msg)
            return False

        return True

    def validate_multi_values(self, val_list: list, validator, prop_name=None) -> bool:
        """Validate a property name using a validator"""
        if self.has_error():
            return False

        try:
            validator(*val_list)
        except ValidationError as err_obj:
            user_msg = f'{err_obj.message} ({prop_name})'
            self.add_err_msg(user_msg)
            return False

        return True

    def check_if_fixed_value_in_categories(self, fixed_value: Any, categories: list) -> bool:
        """Check that the fixed value is in the list of categories"""
        try:
            validate_fixed_value_in_categories(fixed_value, categories)
        except ValidationError as err_obj:
            user_msg = f"{err_obj.message} ('fixed_value')"
            self.add_err_msg(user_msg)
            return False

        return True

    def cast_property_to_float(self, prop_name):
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

    def cast_property_to_int(self, prop_name):
        """Attempt to convert a value to an integer"""
        prop_val = getattr(self, prop_name)

        try:
            prop_val_int = int(prop_val)
        except TypeError:
            self.add_err_msg(f'Failed to convert "{prop_name}" to an integer. (value: "{prop_val}")')
            return False
        except ValueError:
            self.add_err_msg(f'Failed to convert "{prop_name}" to a integer. (value: "{prop_val}")')
            return False

        if isinstance(prop_val, float):
            if prop_val != prop_val_int:
                user_msg = (f'Failed to convert "{prop_name}" to an equivalent integer.'
                            f'(original: {prop_val}, converted: {prop_val_int})')
                self.add_err_msg(user_msg)
                return False

        setattr(self, prop_name, prop_val_int)

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
        try:
            print(json.dumps(self.__dict__, indent=4, cls=DjangoJSONEncoder))
        except TypeError as err_obj:
            print(f'stat_spec.print_debug() failed with {err_obj}')
        # for key, val in self.__dict__.items():
        #    print(f'{key}: {val}')

    def get_short_description_text(self, template_name=None):
        """Get description in plain text"""
        template_name = template_name if template_name else 'analysis/dp_stat_general_description.txt'
        return self.get_short_description_html(template_name)

    def get_short_description_html(self, template_name=None):
        """
        Create an HTML description using a ReleaseInfo object
        """
        slice_length = 10
        value = {}
        # For histogram specs, we need to limit the number of categories and values we display in the front end
        if self.STATISTIC_TYPE == astatic.DP_HISTOGRAM:
            for k, v in self.value.items():
                value[k] = v[:slice_length]
        info_dict = {
            'stat': self,
            'histogram_values': value,
            'use_min_max': 'min' in self.get_prop_validator_keys(),
            'MISSING_VAL_INSERT_FIXED': astatic.MISSING_VAL_INSERT_FIXED,
            'MISSING_VAL_INSERT_RANDOM': astatic.MISSING_VAL_INSERT_RANDOM
        }

        if not template_name:
            template_name = 'analysis/dp_stat_general_description.html'
            # template_name = 'analysis/dp_stat_general_description_tbl.html'

        desc = render_to_string(template_name, info_dict)

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
            "variable_type": self.var_type,
            "result": {
                "value": self.value
            },
            "noise_mechanism": self.noise_mechanism,
            "epsilon": self.epsilon,
            "delta": self.delta,
        })

        # Min/Max
        #
        if 'min' in self.get_prop_validator_keys():
            final_info['bounds'] = OrderedDict({'min': self.min, 'max': self.max})

        # True/False for Boolean
        #
        if 'true_value' in self.get_prop_validator_keys():
            final_info['boolean_values'] = OrderedDict({'true_value': self.true_value,
                                                'false_value': self.false_value})

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

        template_name_html = 'analysis/dp_stat_general_histogram_description.html' \
            if self.STATISTIC_TYPE == astatic.DP_HISTOGRAM else 'analysis/dp_stat_general_description.html'

        template_name_txt = 'analysis/dp_stat_general_histogram_description.txt' \
            if self.STATISTIC_TYPE == astatic.DP_HISTOGRAM else 'analysis/dp_stat_general_description.txt'

        final_info['description']['html'] = self.get_short_description_html(template_name=template_name_html)
        final_info['description']['text'] = self.get_short_description_text(template_name=template_name_txt)

        return final_info

    def get_confidence_level_alpha(self) -> Union[float, None]:
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
        self.error_found = True
        self.error_messages.append(err_msg)

    def add_error_message(self, err_msg: str):
        """Add an error message -- same as "add_err_msg" """
        self.add_err_msg(err_msg)

    @staticmethod
    def _add_double_quotes(value):
        """
        Categories and values need to be enclosed by double
        quotes in order to be handled by OpenDP
        :return:
        """
        # Don't add double quotes if they're already there
        if value.startswith('"') and value.endswith('"'):
            return value

        return f'"{value}"'

    @staticmethod
    def _remove_double_quotes(value):
        """
        Remove double quotes after the DP process
        :return:
        """
        if len(value) < 2:
            return

        # Only remove outermost set of double quotes--may conflict with _add_double_quotes
        #   if the value is supposed to be double_quoted
        #
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return value
