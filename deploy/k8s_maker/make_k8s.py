from dp_utils import get_yyyy_mmdd
from template_formatter import TemplateFormatter
import dpcreator_specs_01 as dpcreator_specs


def make_k8s_template(specs, output_prefix=''):

    # Database
    db_template_name = 'azure_k8s_08_database.yaml'
    tf = TemplateFormatter(specs, db_template_name)
    db_content = tf.formatted_output

    # App
    app_template_name = 'azure_k8s_08_app.yaml'
    output_file = f'{output_prefix}dpcreator.org_08_{get_yyyy_mmdd()}.yaml'

    tf2 = TemplateFormatter(specs, app_template_name)
    app_content = tf2.formatted_output

    full_content = f'{db_content}\n{app_content}'
    TemplateFormatter.write_file_content(full_content, output_file)

if __name__ == '__main__':
    # make_k8s_template()
    make_k8s_template(dpcreator_specs.specs_dev_dpcreator_org, output_prefix='dev.')
    make_k8s_template(dpcreator_specs.specs_demo_dpcreator_org, output_prefix='demo.')
