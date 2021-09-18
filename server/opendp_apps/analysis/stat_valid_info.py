"""
Convenience class for holding statistic validation information
"""


class StatValidInfo:
    """Class to hold the result of a single stat validation"""
    def __init__(self, variable, statistic, valid, message, value=None, accuracy_val=None, accuracy_msg=None):
        """
        :param variable str
        :param statistic str
        :param valid bool
        :param message str              (optional)
        :param accuracy_val float       (optional)
        :param accuracy_msg str         (optional)
        """
        self.variable = variable
        self.statistic = statistic
        self.valid = valid
        self.message = message
        self.value = value
        self.accuracy_val = accuracy_val
        self.accuracy_msg = accuracy_msg


    def as_dict(self):
        """Return as a dict"""
        info = dict(variable=self.variable,
                    statistic=self.statistic,
                    valid=self.valid,
                    message=self.message)

        if self.valid is False:
            return info

        if self.value:
            info['value'] = self.value

        if self.accuracy_val or self.accuracy_msg:
            info['accuracy'] = {}
            if self.accuracy_val:
                info['accuracy']['value'] = self.accuracy_val
            if self.accuracy_msg:
                info['accuracy']['message'] = self.accuracy_msg

        return info


    @staticmethod
    def get_error_msg_dict(variable, statistic, message=None):
        """
        :param variable
        :param statistic
        :param message  (optional)
        """
        return StatValidInfo(variable, statistic, False, message).as_dict()


    @staticmethod
    def get_success_msg_dict(variable, statistic, message=None,
                             accuracy_val=None, accuracy_msg=None):
        """
        :param variable
        :param statistic
        :param message  (optional)
        :param value (optional)
        :param accuracy_val  (optional)
        :param accuracy_msg  (optional)
        """
        return StatValidInfo(variable, statistic, True, message, value=None,
                             accuracy_val=accuracy_val, accuracy_msg=accuracy_msg).as_dict()


    @staticmethod
    def get_success_msg_dict_with_val(variable, statistic, message=None, value=None,
                                      accuracy_val=None, accuracy_msg=None):
        """Return a success message, including the value--actually this shouldn't happen! Value should only be transmitted in a release!"""
        assert False, ("Don't use StatValidInfo.get_success_msg_dict_with_val(...)."
                       " The value should only be available via ReleaseInfo!!!")
        return StatValidInfo(variable, statistic, True, message,
                             value=value, accuracy_val=accuracy_val,
                             accuracy_msg=accuracy_msg).as_dict()

"""
from opendp_apps.analysis.stat_valid_info import StatValidInfo

info = StatValidInfo.get_error_msg(3, 'mean', 'Max is less than Min')
print(info)

{'column_index': 3, 'statistic': 'mean', 'valid': False, 'message': 'Max is less than Min'}

user_msg = ("When the {dist} scale is {scale}, the DP estimate differs from the true value "
             "by no more than {accuracy} at a level-alpha of {alpha}, "
             "or with (1 - {alpha})100% = {perc}% confidence.")
          
StatValidInfo.get_success_msg(4, 'histogram', user_msg, accuracy=0.7)
StatValidInfo.get_success_msg_dict(4, 'histogram', user_msg, accuracy=0.7)

print(info)

"""