def msg(m):
    """
    Shorthand for print statement
    """
    print(m)


def dashes(cnt=40):
    """
    Print dashed line
    """
    msg('-' * cnt)


def msgt(m):
    """
    Add dashed line pre/post print statment
    """
    dashes()
    msg(m)
    dashes()
