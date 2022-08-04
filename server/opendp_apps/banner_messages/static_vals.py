"""
BannerMessage related static vals.
"""

# Depending on the "type" setting, the UI will
#   display the banner with the appropriate styling/icon

BANNER_TYPE_INFORMATIONAL = 'INFO'
BANNER_TYPE_WARNING = 'WARN'
BANNER_TYPE_MODEL_CHOICES = [(BANNER_TYPE_INFORMATIONAL, 'Informational Banner'),
                             (BANNER_TYPE_WARNING, 'Warning Banner')]
BANNER_TYPE_CHOICES = [x[0] for x in BANNER_TYPE_MODEL_CHOICES]
