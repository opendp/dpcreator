import logging
import os

import magic

logger = logging.getLogger(__file__)


class FileExtensionDeterminer(object):

    def __init__(self, filepath):
        """
        Given a filename / filepath, determine the file type via the extension.
        :param filepath: either a string path or a FileField object
        """
        self.filepath = filepath if type(filepath) == str else getattr(filepath, 'path')
        self.filename = None
        self.extension = None

    def get_file_extension(self):
        self.filename, self.extension = os.path.splitext(self.filepath)
        if not self.extension:
            logger.info(f"File {self.filepath} does not contain a file extension. "
                        f"Trying magic to infer the file type.")
            magic_extension = magic.from_file(self.filepath)
            if magic_extension == 'data':
                self.extension = '.dta'
            elif 'SPSS' in magic_extension:
                self.extension = '.sav'
            else:
                self.extension = '.csv'
        return self.extension
