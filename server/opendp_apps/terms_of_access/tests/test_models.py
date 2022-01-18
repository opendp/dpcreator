import os

from django.test import TestCase

from opendp_apps.terms_of_access.models import TermsOfAccess, DifferentTermsOfAccessException


class TestTermsOfAccess(TestCase):
    def test_save_identical_terms(self):
        toa_count = TermsOfAccess.objects.count()
        toa = TermsOfAccess(
            name='test',
            active=True,
            description='''<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <title>Terms of Access</title>
                        </head>
                        <body>
                            You agree to a variety of things.
                        </body>
                        </html>''',
            version='0',
            notes=''
        )
        toa.save(template_path=os.path.dirname(os.path.realpath(__file__)) + f'/templates/0.html')
        self.assertEqual(TermsOfAccess.objects.all().count(), toa_count + 1)

    def test_save_different_formatting(self):
        toa_count = TermsOfAccess.objects.count()
        toa = TermsOfAccess(
            name='test',
            active=True,
            description='''<!DOCTYPE html>
                            <html lang="en">
                            <head>
                            <meta charset="UTF-8">
                            <title> Terms of Access </title>
                            </head><body>
                              You agree to a variety of things.
                            </body></html> ''',
            version='0',
            notes=''
        )
        toa.save(template_path=os.path.dirname(os.path.realpath(__file__)) + f'/templates/0.html')
        self.assertEqual(TermsOfAccess.objects.all().count(), toa_count + 1)

    def test_template_mismatch(self):
        toa = TermsOfAccess(
            name='test',
            active=True,
            description='''<!DOCTYPE html>
                        <html lang="en">
                        <head>
                        <meta charset="UTF-8">
                        <title>Terms of Access</title>
                        </head>
                        <body>
                            You agree to a bunch of new things.
                        </body>
                        </html>''',
            version='0',
            notes=''
        )
        with self.assertRaises(DifferentTermsOfAccessException):
            toa.save(template_path=os.path.dirname(os.path.realpath(__file__)) + f'/templates/0.html')
