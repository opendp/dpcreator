from jinja2 import Template
from jinja2 import PackageLoader, Environment

PARAMS = dict(num_stats=2,
              create_time='Mon, September 9th at 12:00 EST')

def get_intro_para(params=None) -> str:
    if params is None:
        params = PARAMS

    jinja_environment = Environment(loader=PackageLoader('website', 'templates'),
                                    extensions=['jinja2.ext.i18n'])

    # jinja_environment.install_gettext_translations(translation)

    t = Template("""
    {% trans num_stats %}
    Your differentially private statistics is ready. It was created on {{ create_time }}.
    {% pluralize %}
    Your differentially private statistics are ready. They were created on {{ create_time }}.
    {% endtrans %}
    """)
    return t.render(params)
