#!/usr/bin/python

"""Renders DRY documents.

Usage:
  drydoc.py [<filename>] [--encoding=<encoding>] [--output=<output>]
  drydoc.py -h | --help
  drydoc.py --version


Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  -e --encoding=<encoding>  Encoding of the input file.
  -o --output=<output>      Output file.
"""

import os
import sys
import parsers
import templatefunctions

__version__ = '0.1.0'
_PY3 = sys.version_info >= (3, 0)

# Format: {'enginename': (variable_engine, template_engine)}
# Variable engine format: (variable_parse_func, (Exception1, Exception2))
# Template engine format: (TemplateClass, (Exception1, Exception2)
# Exceptions listed in engines are catched, and nicer errors provided. To
# format messages even more, make your own exception class and
# format errors in it.
engines = {}

# Add example engine
engines['example'] = ((parsers.parse_variables, ()),
                      (parsers.Template, ()))

try:
    import yaml
    _YAML = True
except ImportError:
    _YAML = False
    pass

try:
    import jinja2
    _JINJA2 = True

    # This class fixes the issue when trailing newline is removed, when it
    # shouldn't be.
    class FixedJinja2Template(jinja2.Template):
        def __init__(self, text):
            super(FixedJinja2Template, self).__init__(text)
            self.text = text

        def render(self, **kwargs):
            rendered = super(FixedJinja2Template, self).render(**kwargs)
            if self.text[-1] == '\n' and rendered[-1] != '\n':
                rendered += '\n'
            return rendered

except ImportError:
    _JINJA2 = False
    pass

# Add yaml-jinja2 engine
if _YAML and _JINJA2:
    yaml_engine = (yaml.load, ())
    jinja_engine = (FixedJinja2Template, ())
    engines['yj'] = (yaml_engine, jinja_engine)


# Constants
default_encoding = 'utf-8'
section_separator = '\n...\n'
# Variables to pass by default to all templates
template_variables = {}

if _PY3:
    default_engine = 'example'
else:
    default_engine = 'yj'


class AttributeDict(dict):
    """Provides access to items via attributes.
    dictionary.attr == dictionary['attr']
    Beware of keys that are not correct variable names in Python.
    """
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class DryDoc(object):
    def __init__(self, text, engine=engines[default_engine]):
        self.text = text
        self.variable_engine = engine[0][0]
        self.template_engine = engine[1][0]

    def get_variables(self):
        return self._parse_variables()

    def render(self, add_vars=None):
        """Returns rendered text from DRY text.
        You can optionally specify default variables to be sent to template.
        Warning: these default variables override the ones in DRY doc.
        """
        text = self.text
        text_parts = self._split_text(text)
        if len(text_parts) != 2:
            return text

        variables = self.get_variables()
        if add_vars is not None:
            variables.update(add_vars)

        template = text_parts[1]

        t = self.template_engine(template)
        rendered = t.render(**variables).lstrip('\n')
        return rendered

    def _split_text(self, text):
        """Splits text to two parts: variable and template sections.
        It's callers resposibility to check that all parts exist.
        """
        separator = section_separator
        if text.startswith(separator.lstrip()):
            separator = separator.lstrip()
        text_parts = text.split(separator, 1)
        return text_parts

    def _parse_variables(self):
        """Parses variables from text and returns them in dict format."""
        variables = {}
        text_parts = self._split_text(self.text)
        if len(text_parts) != 2:
            return variables

        top_section = text_parts[0].strip()

        if len(top_section):
            variables = self.variable_engine(top_section)

        d = AttributeDict()
        try:
            d.update(variables)
        except TypeError:
            path = self.filepath
            raise TypeError('Check syntax of variables in \'%s\'' % path)

        return d


def read_file(filepath, encoding=default_encoding):
    """Reads file's contents and returns unicode."""
    open_func = open
    if _PY3:
        open_func = lambda f, mode: open(f, mode, encoding=encoding)

    with open_func(filepath, 'r') as f:
        content = f.read()

    if not _PY3:
        content = content.decode(encoding, errors='replace')

    return content


def write_file(text, filepath, encoding=default_encoding):
    """Writes unicode to file with specified encoding."""
    open_func = open
    if _PY3:
        open_func = lambda f, mode: open(f, mode, encoding=encoding)
    else:
        text = text.encode(encoding, errors='replace')

    with open_func(filepath, 'w') as f:
        f.write(text)


def inputfile_dir(filename):
    """Returns the directory where given inputfile is located."""
    inputfile_path = os.path.abspath(os.path.join(os.getcwd(), filename))
    inputfile_dir = os.path.split(inputfile_path)[0]
    return inputfile_dir


def main():
    from docopt import docopt
    arguments = docopt(__doc__, argv=sys.argv[1:],
                       help=True, version=__version__)

    encoding = arguments['--encoding']
    if encoding is None:
        encoding = default_encoding

    # Read drydoc in from whatever source

    filename = arguments['<filename>']
    if filename is not None:
        try:
            text = read_file(filename)
        except IOError as e:
            print('Could not open file. %s' % e)
            sys.exit(1)
    else:
        # This makes it possible to use via pipe e.g. x | python drydoc.py
        text = sys.stdin.read()

    # Parse and render the drydoc

    if default_engine == 'yj':
        # Add functions for jinja2 templates
        if filename is None:
            drydocdir = os.getcwd()
        else:
            drydocdir = inputfile_dir(filename)

        info = {'drydocdir': drydocdir, 'encoding': encoding,
                'engine': engines[default_engine],
                'inputfile': filename}

        funcs = templatefunctions.get_funcs(info)
        template_variables.update(funcs)

        info['template_vars'] = template_variables

    engine = engines[default_engine]
    doc = DryDoc(text)

    try:
        rendered_text = doc.render(add_vars=template_variables)
    except engine[0][1] as e:
        print('Error parsing variables: %s' % str(e).capitalize())
        sys.exit(1)
    except engine[1][1] as e:
        print('Error parsing template: %s' % str(e).capitalize())
        sys.exit(1)

    # Output the rendered text to where ever

    output = arguments['--output']
    if output is not None:
        try:
            write_file(rendered_text, output, encoding=encoding)
        except IOError as e:
            print('Could not open file. %s' % e)
            sys.exit(1)
    else:
        if _PY3:
            sys.stdout.write(rendered_text)
        else:
            sys.stdout.write(rendered_text.encode(encoding, errors='replace'))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Quit.')
