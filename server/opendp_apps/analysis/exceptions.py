

class EpsilonNotSetException(Exception):
    """Raised when the epsilon on an Analysis Plan is not set"""
    pass


class AllottedEpsilonExceedsLimit(Exception):
    """Exception raised the epsilon in AnalysisPlan objects exceeds the overall epsilon in DepositorSetupInfo"""
    pass
