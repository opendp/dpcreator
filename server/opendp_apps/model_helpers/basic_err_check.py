"""
An object with some basic methods for capturing errors
"""

class BasicErrCheck():

    error_found = False
    error_message = None

    def has_error(self):
        """Did an error occur?"""
        return self.error_found

    def get_error_message(self):
        """Return the error message if 'has_error' is True"""
        assert self.has_error(),\
            "Please check that '.has_error()' is True before using this method"

        return self.error_message

    def get_err_msg(self):
        """Return the error message if 'has_error' is True"""
        return self.get_error_message()

    def add_err_msg(self, err_msg):
        """Add an error message"""
        self.error_found = True
        self.error_message = err_msg

    def add_error_message(self, err_msg):
        """Add an error message -- same as "add_err_msg" """
        self.add_err_msg(err_msg)


class BasicErrCheckList():

    error_found = False
    error_messages = []

    def has_error(self):
        """Did an error occur?"""
        return self.error_found

    def get_error_messages(self):
        """Return the error message if 'has_error' is True"""
        assert self.has_error(),\
            "Please check that '.has_error()' is True before using this method"

        return self.error_messages

    def get_err_msgs(self):
        """Return the error message if 'has_error' is True"""
        return self.get_error_messages()

    def get_err_msgs_concat(self, sep_char=' '):
        return f'{sep_char}'.join(self.get_error_messages())

    def get_error_messages_concat(self, sep_char=' '):
        return self.get_err_msgs_concat(sep_char)

    def add_err_msg(self, err_msg):
        """Add an error message"""
        # print('add err:', err_msg)
        self.error_found = True
        self.error_messages.append(err_msg)

    def add_error_message(self, err_msg):
        """Add an error message -- same as "add_err_msg" """
        self.add_err_msg(err_msg)


def try_it():
    """quick check"""
    b = BasicErrCheck()
    print('error_found', b.error_found)
    print('error_message', b.error_message)
    print(b.has_error())
    b.add_err_msg('uh oh')
    print(b.has_error())
    print(b.get_error_message())

if __name__ == '__main__':
    try_it()
