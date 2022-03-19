"""
Given a Release object, send an email with attached PDF/JSON files
"""
from mimetypes import guess_type
from os.path import basename

from django.db.models.fields.files import FieldFile
from django.contrib.sites.models import Site
from django.conf import settings
from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string

from opendp_apps.model_helpers.basic_err_check import BasicErrCheck
from opendp_apps.analysis.models import ReleaseInfo


class ReleaseEmailUtil(BasicErrCheck):

    def __init__(self, release_info: ReleaseInfo, alternate_to_email=None):
        """Init with a ReleaseInfo object"""
        self.release_info = release_info
        self.alternate_to_email = alternate_to_email

        self.dataset = release_info.dataset

        self.current_site = None
        self.analysis_plan = None
        self.num_stats = None

        self.has_pdf_file = False
        self.has_json_file = False

        self.run_email_process()

    def run_email_process(self):
        """Assemble the data and send the email"""
        if self.has_error():
            return

        self.current_site = Site.objects.first()

        self.analysis_plan = self.release_info.analysisplan_set.first()
        if not self.analysis_plan:
            self.add_err_msg('Failed to retrieve the AnalysisPlan object')

        if not self.release_info.dp_release:
            self.add_err_msg('Email error, within the release object, "dp_release" has no data.')
            return

        if 'statistics' not in self.release_info.dp_release:
            self.add_err_msg('Email error, "dp_release" has no "statistics".')
            return

        self.num_stats = len(self.release_info.dp_release['statistics'])

        if self.release_info.dp_release_json_file:
            self.has_json_file = True

        if self.release_info.dp_release_pdf_file:
            self.has_pdf_file = True

        if settings.DPCREATOR_USING_HTTPS:
            site_scheme = 'https://'
        else:
            site_scheme = 'http://'

        info_dict = {"username": self.analysis_plan.analyst.username,
                     "num_stats": self.num_stats,
                     "dataset": self.dataset,
                     "site_scheme": site_scheme,
                     "current_site": self.current_site,
                     "has_pdf_file": self.has_pdf_file,
                     "has_json_file": self.has_json_file,
                     }

        subject = f'DP Release ready for {self.dataset.name}'
        email_content = render_to_string('analysis/email/release_complete_email.txt',
                                         info_dict)

        self.create_and_send_mail(subject, email_content)

    def create_and_send_mail(self, subject: str, email_content: str):
        """Send the email"""
        if self.has_error():
            return

        if self.alternate_to_email:
            to_email = self.alternate_to_email
        else:
            to_email = self.analysis_plan.analyst.email

        msg = EmailMessage(subject=subject,
                           body=email_content,
                           from_email=settings.DEFAULT_FROM_EMAIL,
                           to=[to_email])

        # Attach files
        if self.has_pdf_file:
            self.attach_file_to_email(msg,
                                      self.release_info.dp_release_pdf_file)

        if self.has_json_file:
            self.attach_file_to_email(msg,
                                      self.release_info.dp_release_json_file)

        msg.send(fail_silently=not settings.DEBUG)

    def attach_file_to_email(self, email_msg: EmailMessage, file_field: FieldFile):
        """Attach the file in the Django file field to the email_msg"""
        if self.has_error():
            return

        if not file_field:
            self.add_err_msg((f'Failed to attach file to email.'
                              f' file_field: {file_field}'))
            return

        try:
            email_msg.attach(basename(file_field.name),
                             file_field.read(),
                             guess_type(file_field.name)[0])
        except OSError as ex_obj:
            user_msg = 'Error attaching the PDF release file. {ex_obj}'
            self.add_err_msg(user_msg)
        except TypeError as ex_obj:
            user_msg = 'Error attaching the PDF release file. {ex_obj}'
            self.add_err_msg(user_msg)
        except IndexError as ex_obj:
            user_msg = 'Error attaching the PDF release file. {ex_obj}'
            self.add_err_msg(user_msg)


"""
docker-compose run server python manage.py shell

from opendp_apps.analysis.release_email_util import ReleaseEmailUtil
from opendp_apps.analysis.models import ReleaseInfo

r = ReleaseInfo.objects.get(id=1)
util = ReleaseEmailUtil(r)
if util.has_error():
  print('Uh oh!!')
  print(r.get_err_msg())
else:
  print('email sent')
"""