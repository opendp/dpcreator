"""
This has the required interface as StatSpec but is only used to hold
a spec-level error when there isn't enough info for a minimal spec

It simply holds an error message. If you also send data, it skips any validation.

Minimal example: `spec = DPSpecError(error_message="Something wrong")`

With other props:
    props = {
             "error_message": "Couldn't find variable_info",  # required!
             "variable": "education_level",
             "statistic": DP_MEAN,
             "epsilon": 0.25,
             #.... (as much as more info as desired) ...
             }
    spec = DPSpecError(props)     # skips all validation and sets `self.error_found = True`

"""
from opendp_apps.analysis.tools.stat_spec import StatSpec
from opendp_apps.analysis import static_vals as astatic


class DPSpecError(StatSpec):

    ERR_MSG_REQUIRED_PROPS = ('It is required that "props" has an "error_message".'
                              'e.g.: `spec = DPSpecError(error_message="Something wrong")`')
    """
    This is used to hold an error message!
    """
    def __init__(self, props: dict):
        """
        Minimum format for props
        {
            "error_message": "The error to send to the user"
        }
        """
        super().__init__(props)

        assert 'error_message' in props, self.ERR_MSG_REQUIRED_PROPS

        self.add_err_msg(props['error_message'])    # Sets `self.error_found = True`


    def run_02_basic_validation(self):
        """Unusual override!!!"""
        pass

    #
    # The methods below fields are required, e.g. @abc.abstract
    #   on the parent class
    #

    def additional_required_props(self):
        return []

    def run_01_initial_handling(self):
        pass

    def run_03_custom_validation(self):
        pass

    def check_scale(self, scale, preprocessor, dataset_distance):
        pass

    def get_preprocessor(self):
        return None

    def run_chain(self, columns: list, file_obj, sep_char=","):
        return False

    def set_accuracy(self):
        pass
