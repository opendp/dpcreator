"""Constants used to identify file extensions and get mime types"""
import os

CSV_FILE_EXT = '.csv'
TAB_FILE_EXT = '.tab'
TAB_FILE_EXT2 = '.tsv'
XLS_FILE_EXT = '.xls'
XLSX_FILE_EXT = '.xlsx'

ACCEPTABLE_FILE_TYPE_EXTS = (CSV_FILE_EXT,
                             TAB_FILE_EXT,
                             TAB_FILE_EXT2,
                             XLS_FILE_EXT,
                             XLSX_FILE_EXT)

ACCEPTABLE_EXT_LIST = ', '.join(['"%s"' % x for x in ACCEPTABLE_FILE_TYPE_EXTS])

MIME_TYPE_PAIRS = (\
    (CSV_FILE_EXT, 'text/csv'),
    (TAB_FILE_EXT, 'text/tab-separated-values'),
    (TAB_FILE_EXT2, 'text/tab-separated-values'),
    (XLS_FILE_EXT, 'application/vnd.ms-excel'),
    (XLSX_FILE_EXT, ('application/vnd.openxmlformats-officedocument'
                     '.spreadsheetml.sheet')),)

MIME_TYPE_LOOKUP = {x:y for x, y in MIME_TYPE_PAIRS}

def get_mime_type(file_ext, unknown_text=None):
    """Return a mimetype based on an extension."""
    if not unknown_text:
        unknown_text = "Unknown mime type for extension: %s" % file_ext
    return MIME_TYPE_LOOKUP.get(\
                file_ext.lower(),
                unknown_text)

def get_data_file_separator(fname):
    """Based on the extension, get the correct separator, default to ',' """
    filename, file_extension = os.path.splitext(fname)
    file_extension = file_extension.lower()
    if file_extension in [TAB_FILE_EXT, TAB_FILE_EXT2]:
        return '\t'
    elif file_extension == CSV_FILE_EXT:
        return ','
    return ','
