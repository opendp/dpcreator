"""
Basic class to hold a single streaming message returned by a TA2
"""
from collections import OrderedDict
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from opendp_apps.async_messages import static_vals as mstatic
from opendp_apps.async_messages.consumers import ChatConsumer


class WebsocketMessage(object):
    """Basic message sent back via a websocket"""

    def __init__(self, msg_type, success, user_message, msg_cnt=None, data=None, **kwargs):
        assert success in (True, False), 'success must be True or False'

        self.msg_type = msg_type  # e.g. GetSearchSolutionsResults
        self.success = success
        self.user_message = user_message
        self.msg_cnt = msg_cnt
        self.data = data  # e.g. python OrderedDict
        self.timestamp = datetime.now()
        self.additional_args = kwargs

    def __repr__(self):
        """print representation"""
        return '%s (success: %s)' % (self.msg_type, self.success)

    def send_message(self, websocket_id):
        """Send the message over a websocket"""
        channel_layer = get_channel_layer()

        group_name = ChatConsumer.get_group_name(websocket_id)

        async_to_sync(channel_layer.group_send)( \
            group_name,
            dict(type=mstatic.MESSAGE_TYPE,
                 message=self.as_dict()))

    @staticmethod
    def get_success_message(msg_type, user_message, msg_cnt=None, data=None, **kwargs):
        """Prefill the success to True"""
        return WebsocketMessage(msg_type=msg_type,
                                success=True,
                                user_message=user_message,
                                message=user_message,
                                msg_cnt=msg_cnt,
                                data=data,
                                **kwargs)

    @staticmethod
    def get_fail_message_with_data(msg_type, user_message, **kwargs):
        """Prefill the success to True, assumes no data"""
        data = kwargs.get('data', None)

        return WebsocketMessage(msg_type=msg_type,
                                success=False,
                                user_message=user_message,
                                message=user_message,
                                data=data)

    @staticmethod
    def get_fail_message(msg_type, user_message, msg_cnt=None):
        """Prefill the success to True, assumes no data"""
        return WebsocketMessage(msg_type=msg_type,
                                success=False,
                                user_message=user_message,
                                message=user_message,
                                msg_cnt=msg_cnt)

    def as_dict(self):
        """Return in dict format"""
        od = OrderedDict()
        attrs = ['msg_type', 'timestamp',
                 'msg_cnt', 'success',
                 'user_message', 'data']
        for item in attrs:
            val = self.__dict__.get(item, None)
            if val is None:
                continue

            if item == 'timestamp':
                val = val.strftime('%Y-%m-%dT%H:%M:%S')

            od[item] = val

        if self.additional_args:
            od2 = OrderedDict()
            for k, val2 in self.additional_args.items():
                od2[k] = val2
            od['additional_info'] = od2
        return dict(od)
