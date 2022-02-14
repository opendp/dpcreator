"""
Allow deletion of data in between cypress tests
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from opendp_apps.analysis.models import DepositorSetupInfo

class Command(BaseCommand):
    help = "Delete test instances of DepositorSetupInfo and related objects via specific UUIDs"

    def handle(self, *args, **options):
        """
        This is a hack/quick fix for issue:
        https://github.com/opendp/dpcreator/issues/505
        """
        user_msg = ('Preparing to delete test instances of DepositorSetupInfo'
                    ' and related objects via specific UUIDs. (This is a hack until this'
                    ' issue is fixed: https://github.com/opendp/dpcreator/issues/505)')
        self.stdout.write(self.style.SUCCESS(user_msg))

        # Note: The uuid's below may be found in multiple fixtures
        #
        object_ids_for_deletion = ['f454732a-ac44-40c8-a2c3-baaa9f4756a9', # pk 3 - depositorsetupinfo
                                   '9255c067-e435-43bd-8af1-33a6987ffc9b', # pk 1 - depositorsetupinfo
                                   '4d5be3e0-34d0-4bdc-be79-10f27f19e293', # pk 4 - depositorsetupinfo
                                   ]
        num_objects_to_delete = len(object_ids_for_deletion)

        qs = DepositorSetupInfo.objects.filter(object_id__in=object_ids_for_deletion)
        if qs.count() != num_objects_to_delete:
            user_msg = (f"Expected {num_objects_to_delete} DepositorSetupInfo'"
                        f" objects but found {qs.count()}")
            self.stdout.write(self.style.ERROR(user_msg))
            return

        (del_cnt, obj_del_cnts) = qs.delete()
        if not isinstance(obj_del_cnts, dict):
            user_msg = (f"Deletion failed for an unknown reason.")
            self.stdout.write(self.style.ERROR(user_msg))
            return

        depositor_objects_deleted = obj_del_cnts.get('analysis.DepositorSetupInfo', 0)
        if depositor_objects_deleted != num_objects_to_delete:
            user_msg = (f"Attempted to delete {num_objects_to_delete} DepositorSetupInfo'"
                        f" objects but deleted {del_cnt}")
            self.stdout.write(self.style.ERROR(user_msg))
            return

        for model_name, dcnt in obj_del_cnts.items():
            user_msg = f'Deleted {dcnt} "{model_name}" objects.'
            self.stdout.write(self.style.SUCCESS(user_msg))

        user_msg = (f"Success!")
        self.stdout.write(self.style.SUCCESS(user_msg))

