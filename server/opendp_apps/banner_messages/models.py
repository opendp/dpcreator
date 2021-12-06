from collections import OrderedDict
from datetime import datetime

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

from opendp_apps.banner_messages import static_vals as bstatic
from opendp_apps.model_helpers.models import TimestampedModelWithUUID

class BannerMessage(TimestampedModelWithUUID):
    """
    "active" banner messages are displayed in the DP Creator header area
    """
    name = models.CharField(max_length=255, help_text='For internal reference, not displayed')
    active = models.BooleanField(default=True, help_text='Set to True to display banner')
    type = models.CharField(max_length=128,
                            choices=bstatic.BANNER_TYPE_MODEL_CHOICES,
                            help_text='Used by the UI to determine display formatting')
    sort_order = models.IntegerField(default=1,
                                     help_text=('Relative sort order if there'
                                                ' is more than 1 active banner.'))

    # user who initially added/uploaded data
    editor = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.PROTECT,
                                blank=True,
                                null=True,
                                help_text='auto-filled on save')

    content = models.TextField(help_text='Banner content. May contain basic HTMl tags: links, boldface, etc.')


    is_timed_message = models.BooleanField(
                        default=False,
                        help_text=('Optional. If True, use "active" as well as both'
                                   ' "view_start_time"/"view_stop_time" settings to determine banner display.'))

    view_start_time = models.DateTimeField(blank=True,
                                      null=True,
                                      help_text=('Optional. Used in conjunction with' 
                                                 ' "is_timed_message" and "view_stop_time"'))

    view_stop_time = models.DateTimeField(blank=True,
                                      null=True,
                                      help_text=('Optional. Used in conjunction with' 
                                                 ' "is_timed_message" and "view_start_time"'))

    class Meta:
        db_table = "banner_messages"
        verbose_name = 'Banner Message'
        verbose_name_plural = 'Banner Messages'
        ordering = ('active', 'sort_order', '-created')

    def __str__(self):
        return self.name


    def clean(self):
        """Validation checks for view_start_time/view_stop_time and is_timed_message"""
        req_both_times = ('The "View Start Time" and "View Stop Time"'
                          ' must both be set--or do not set either field')

        if self.view_start_time and not self.view_stop_time:
            raise ValidationError(req_both_times)

        if self.view_stop_time and not self.view_start_time:
            raise ValidationError(req_both_times)

        if self.view_stop_time and self.view_start_time:
            if not self.is_timed_message:
                raise ValidationError(('If using the "View Start Time" and "View Stop Time",'
                                       ' set "Is Timed Message" to True'))
            if self.view_stop_time < self.view_start_time:
                raise ValidationError(('The "View Start Time" must be before the'
                                       ' "View Stop Time"'))

        if self.is_timed_message:
            if not (self.view_stop_time and self.view_start_time):
                raise ValidationError(('If using "Is Timed Message", set the'
                                       ' "View Start Time" and "View Stop Time"'))


    def as_dict(self) -> OrderedDict:
        """
        Return as dict
        """
        info = OrderedDict(dict(id=self.id,
                    name=str(self.name),
                    type=self.type,
                    sort_order=self.sort_order,
                    content=self.content,
                    is_timed_message=self.is_timed_message,
                    updated=str(self.updated),
                    created=str(self.created),
                    object_id=self.object_id.hex))

        return info

    def save_as_inactive(self) -> bool:
        """Set the given banner_message to inactive"""
        self.active = False
        self.save()

        return True


    '''
    def is_valid_time_window(self, current_time: datetime=None) -> bool:
        """
        Used for messages with specific start/end times.
        To be True, the following conditions must be met:
        - active -> True
        - use_start_end_times -> True
        - view_start_time -> view_start_time is >= current time
        - view_stop_time -> view_stop_time <= current time
        """
        if not(self.active and self.use_start_end_times):
            return False

        if self.view_start_time and self.view_stop_time:
            if not current_time:
                current_time = datetime.now()

            if self.view_start_time >= current_time and self.view_stop_time <= current_time:
                return True

        return False
    '''