"""
Convenience classes for returning multiple values from functions

Examples:
    Success w/ data: return ok_resp(some_obj)
    Success w/ data and a message: return ok_resp(some_obj, 'It worked')

    Error w/ message: return err_resp('some error message')
    Error w/ message and data: return err_resp('some error message', dict(failed_lines=[45, 72])


"""


class BasicResponse:

    def __init__(self, success, message=None, data=None):
        """
        Initialize
        """
        assert success in (True, False), "Success must be a Python boolean"
        self.success = success
        self.message = message
        self.data = data

    def as_dict(self):
        """
        Return as a Python dict
        - Can be sent back as a Django JSONResponse
        """
        info = dict(success=self.success)
        if self.message:
            info['message'] = self.message
        if self.data:
            info['data'] = self.data

        return info

    def is_success(self):
        """
        Can also use .success
        """
        return self.success


def ok_resp(data, message=None):
    """Return a SuccessResponse with success=True and data"""
    return BasicResponse(True, message=message, data=data)


def err_resp(err_msg, data=None):
    """Return a ErrorResponse with success=False and err_msg"""
    return BasicResponse(False, message=err_msg, data=data)


if __name__ == '__main__':
    br = ok_resp(dict(median=34))
    print(br.as_dict())
    br = ok_resp(dict(median=34), 'it worked!')
    print(br.as_dict())

    br = err_resp('did not go so well')
    print(br.as_dict())
    br = err_resp('did not go so well', dict(failed_term=45))
    print(br.as_dict())
