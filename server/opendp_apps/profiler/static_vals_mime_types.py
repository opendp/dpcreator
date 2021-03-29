"""Constants used to identify file extensions and get mime types"""

CSV_FILE_EXT = '.csv'
TAB_FILE_EXT = '.tab'
XLS_FILE_EXT = '.xls'
XLSX_FILE_EXT = '.xlsx'

ACCEPTABLE_FILE_TYPE_EXTS = (CSV_FILE_EXT,
                             TAB_FILE_EXT,
                             XLS_FILE_EXT,
                             XLSX_FILE_EXT)

ACCEPTABLE_EXT_LIST = ', '.join(['"%s"' % x for x in ACCEPTABLE_FILE_TYPE_EXTS])

MIME_TYPE_PAIRS = (\
    (CSV_FILE_EXT, 'text/csv'),
    (TAB_FILE_EXT, 'text/tab-separated-values'),
    (XLS_FILE_EXT, 'application/vnd.ms-excel'),
    (XLSX_FILE_EXT, ('application/vnd.openxmlformats-officedocument'
                     '.spreadsheetml.sheet')),)

MIME_TYPE_LOOKUP = {x:y for x, y in MIME_TYPE_PAIRS}

def get_mime_type(file_ext):
    """Return a mimetype based on an extension."""
    return MIME_TYPE_LOOKUP.get(\
                file_ext.lower(),
                "Unknown mime type for extension: %s" % file_ext)

