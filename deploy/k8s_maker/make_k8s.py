from dp_utils import get_yyyy_mmdd
from template_formatter import TemplateFormatter
import dpcreator_specs_01 as specs_01


def make_k8s_template(specs, output_prefix=''):

    # Database
    db_template_name = 'azure_k8s_06_database.yaml'
    tf = TemplateFormatter(specs, db_template_name)
    db_content = tf.formatted_output

    # App
    app_template_name = 'azure_k8s_06_app.yaml'
    output_file = f'{output_prefix}dpcreator_06_{get_yyyy_mmdd()}.yaml'

    tf2 = TemplateFormatter(specs, app_template_name)
    app_content = tf2.formatted_output

    full_content = f'{db_content}\n{app_content}'
    TemplateFormatter.write_file_content(full_content, output_file)

if __name__ == '__main__':
    # make_k8s_template()
    make_k8s_template(specs_01.specs_01)
    make_k8s_template(specs_01.specs_01_test, output_prefix='test_')

