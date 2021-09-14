"""
Convenience class for holding statistic validation information
"""


class StatValidInfo:
    """Class to hold the result of a single stat validation"""
    def __init__(self, var_name: str, statistic: str, valid: bool, message: str=None, value=None, accuracy: float=None):
        self.var_name = var_name
        self.statistic = statistic
        self.valid = valid
        self.message = message
        self.value = value
        self.accuracy = accuracy

    def as_dict(self):
        """Return as a dict"""
        info = dict(var_name=self.var_name,
                        statistic=self.statistic,
                        valid=self.valid,
                        message=self.message)

        if self.valid is False:
            return info

        # info['value'] = self.value
        if self.accuracy:
            info['accuracy'] = self.accuracy

        return info

    @staticmethod
    def get_error_msg(var_name, statistic, message=None):
        return StatValidInfo(var_name, statistic, False, message)

    @staticmethod
    def get_error_msg_dict(var_name, statistic, message=None):
        return StatValidInfo.get_error_msg(var_name, statistic, message).as_dict()

    @staticmethod
    def get_success_msg(var_name, statistic, message=None, value=None, accuracy=None):
        return StatValidInfo(var_name, statistic, True, message, value, accuracy)

    @staticmethod
    def get_success_msg_dict(var_name, statistic, message=None, value=None, accuracy=None):
        return StatValidInfo.get_success_msg(var_name, statistic, message, value, accuracy).as_dict()

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