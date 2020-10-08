from django.db import models

from opendp_apps.dataverse.models import DataverseFile
from opendp_apps.user.models import Session, Group, DataverseUser


class DataSet(models.Model):
    """
    Placeholder until we have more details
    about what a dataset should contain
    """
    # Creator dataset
    user = models.ForeignKey(DataverseUser, on_delete=models.CASCADE)


class Computation(models.Model):
    """
    Represents a single transformation / calculation
    in an analysis
    """
    pass


class AnalysisPlan(models.Model):
    """
    Outlines the steps for the analysis
    """
    user = models.ForeignKey(DataverseUser, on_delete=models.CASCADE)
    data_set = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    computations = models.ManyToManyField(Computation)


class DPRequest(models.Model):
    """
    Initiates an analysis
    """
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

    class AnalysisTypes(models.TextChoices):
        ONE = 'EX1', 'Example 1'
        TWO = 'EX2', 'Example 2'
    analysis_type = models.CharField(max_length=128, choices=AnalysisTypes.choices)


class DPRelease(models.Model):
    """
    Record the release of a DP analysis
    """
    # Who initiated the release
    user = models.ForeignKey(DataverseUser, on_delete=models.CASCADE)

    # Group(s) with view access to the release
    group = models.ManyToManyField(Group)

    # Stores epsilon, etc.
    dataverse_file = models.ForeignKey(DataverseFile, on_delete=models.CASCADE)
