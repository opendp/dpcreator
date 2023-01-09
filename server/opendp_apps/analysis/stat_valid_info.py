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
