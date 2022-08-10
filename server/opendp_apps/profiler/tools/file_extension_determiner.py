import logging
import os

import magic

logger = logging.getLogger(__file__)


class FileExtensionDeterminer(object):

    def __init__(self, filepath=None, file_obj=None):
        """
        Given a filename / filepath, determine the file type via the extension.
        :param filepath: either a string path or a FileField object
        """
        if filepath and file_obj:
            raise ValueError("Only one of ['filepath', 'file_obj'] should be given.")
        self.filepath = None
        self.file_obj = None
        if filepath:
            self.filepath = filepath if type(filepath) == str else getattr(filepath, 'path')
        else:
            self.file_obj = file_obj
        self.filename = None
        self.extension = None

    def get_file_extension(self):
        if self.filepath:
            self.filename, self.extension = os.path.splitext(self.filepath)
            logger.info(f"self.filename, self.extension = {self.filename}, {self.extension}")
            if self.extension:
                return self.extension
            else:
                logger.info(f"File {self.filepath} does not contain a file extension. "
                            f"Trying magic to infer the file type.")
                magic_extension = magic.from_file(self.filepath)
        else:
            magic_extension = magic.from_buffer(self.file_obj)

        if magic_extension:
            if magic_extension == 'data':
                self.extension = '.dta'
            elif 'SPSS' in magic_extension:
                self.extension = '.sav'
        else:
            self.extension = '.csv'

        return self.extension
