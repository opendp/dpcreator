from collections import OrderedDict
import json
import os
from os.path import isdir, isfile, join

import jinja2

from settings import TEMPLATES_DIR, OUTPUT_DIR
from dp_utils import msgt


class TemplateFormatter():

    def __init__(self, template_dict, k8s_template_name, **kwargs):
        """execute main method"""
        self.output_filename = kwargs.get('output_filename', None)

        self.template_obj = None
        self.formatted_output = None

        # Initialize the Jinja template
        self.setup_template(k8s_template_name)

        # Render the template
        self.render_template(template_dict)


    def setup_template(self, k8s_template_name):
        """Create a the jinja template"""

        templateLoader = jinja2.FileSystemLoader(searchpath=TEMPLATES_DIR)
        templateEnv = jinja2.Environment(loader=templateLoader)

        # Default template file used
        self.template_obj = templateEnv.get_template(k8s_template_name)
        #self.template_obj_single_paper = templateEnv.get_template('single_paper.html')


    def render_template(self, template_dict):
        """Make a simple template and write it to the output directory"""
        assert isinstance(template_dict, dict), 'template_dict must be a Python dict'

        self.formatted_output = self.template_obj.render(template_dict)

        # If an output_file_name name is given, write the output
        #
        if self.output_filename:
            fullname = join(OUTPUT_DIR, self.output_filename)
            with open(fullname, 'w') as fh:
                fh.write(self.formatted_output)
            msgt(f'file written: {fullname}')

    @staticmethod
    def write_file_content(content, filename):
        """write to a file..."""
        fullname = join(OUTPUT_DIR, filename)
        with open(fullname, 'w') as fh:
            fh.write(content)
        msgt(f'file written: {fullname}')