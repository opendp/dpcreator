"""
This has the required interface as StatSpec but is only used to hold
a spec-level error -- nothing else works!
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


        self.add_err_msg(props['error_message'])


    def run_basic_validation(self):
        """Unusual override!!!"""
        pass

    #
    # The methods below fields are required, e.g. @abc.abstract
    #   on the parent class
    #

    def additional_required_props(self):
        return []

    def run_initial_handling(self):
        pass

    def run_custom_validation(self):
        pass

    def check_scale(self, scale, preprocessor, dataset_distance):
        pass

    def get_preprocessor(self):
        return None

    def run_chain(self, columns: list, file_obj, sep_char=","):
        return False

    def set_accuracy(self):
        pass
