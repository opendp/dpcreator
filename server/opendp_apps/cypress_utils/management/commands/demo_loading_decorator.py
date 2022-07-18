import logging

from django.conf import settings

from opendp_apps.cypress_utils import static_vals as cystatic

logger = logging.getLogger(__file__)


def check_allow_demo_loading(func):
    def inner(*args, **kwargs):
        # Important check!!
        if not settings.ALLOW_DEMO_LOADING:  # Do not remove this check
            logger.error(cystatic.MESSAGE_CLEAR_DATA_CMD_ERR)
            return
        return func(*args, **kwargs)

    return inner
