"""
Example parsers for DRY document.
They are very very simple for demonstration purposes.

Setting variable_engine=parse_variables() and template_engine=Template()
in drydoc.py would
"""


example_doc = """
a = testing..
b = 1
...
This is {{ a }}
Variable b is {{ b }}.
"""


def parse_variables(text):
    d = {}
    for line in text.strip().split('\n'):
        key, value = line.split('=')
        d[key.strip()] = value.strip()
    return d


class Template(object):
    def __init__(self, text):
        self.text = text

    def render(self, **kwargs):
        rendered_text = self.text
        for key, value in kwargs.items():
            key = u'{{ %s }}' % key.lower()
            rendered_text = rendered_text.replace(key, value)
        return rendered_text
