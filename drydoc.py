#!/usr/bin/python

"""Renderes DRY documents.

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

__version__ = '0.0.1'


import os
import sys
import parsers


# Format: {name_of_engine: (variable_parse_func, (Exception1, Exception2))}
variable_engines = {}
# Format: {name_of_engine: (TemplateClass, (Exception1, Exception2))}
template_engines = {}

# Exceptions listed in engines are catched, and nicer errors provided. To
# format messages even more, make your own exception class and
# format errors in it.

# Import example engines.
variable_engines['example'] = (parsers.parse_variables, (ValueError))
template_engines['example'] = (parsers.Template, ())

try:
    import yaml
    variable_engines['yaml'] = (yaml.load, (yaml.reader.ReaderError,
                                            TypeError))
except ImportError:
    pass

try:
    import jinja2
    template_engines['jinja2'] = (jinja2.Template, ())
except ImportError:
    pass


# Constants
_PY3 = sys.version_info >= (3, 0)
default_encoding = 'utf-8'
section_separator = '\n...\n'
# Variables to pass by default to all templates
template_variables = {}


class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


def read_file(filepath, encoding=default_encoding):
    open_func = open
    if _PY3:
        open_func = lambda f, mode: open(f, mode, encoding=encoding)

    with open_func(filepath, 'r') as f:
        content = f.read()

    if not _PY3:
        content = content.decode(encoding)

    return content


def write_file(text, filepath, encoding=default_encoding):
    open_func = open
    if _PY3:
        open_func = lambda f, mode: open(f, mode, encoding=encoding)
    else:
        text = text.encode(encoding)

    with open_func(filepath, 'w') as f:
        f.write(text)


def variables_from_file(filepath, originaldir, variable_engine,
                        encoding=default_encoding):
    """Returns variables dictionary from a DRY document.
    originaldir is the directory where the original DRY document is
    located.
    """
    filepath = os.path.abspath(os.path.join(originaldir, filepath))

    variables = {}
    dry_text = read_file(filepath, encoding=encoding)
    text_parts = dry_text.split(section_separator, 1)
    if len(text_parts) != 2:
        return variables

    top_section = text_parts[0].strip()

    if len(top_section):
        variables = variable_engine(top_section)

    d = AttributeDict()
    try:
        d.update(variables)
    except TypeError:
        raise TypeError('Check syntax of variables in \'%s\'' % filepath)

    return d


def render_dry_text(dry_text, variable_engine, template_engine,
                    add_variables=None):
    """Returns rendered text from DRY text. dry_text must be unicode.
    You can optionally specify default variables.
    """
    text_parts = dry_text.split(section_separator, 1)
    if len(text_parts) != 2:
        return dry_text

    variables = text_parts[0].strip()
    template = text_parts[1]

    if not len(variables):
        variables = {}
    else:
        variables = variable_engine(variables)

    if add_variables is not None:
        try:
            variables.update(add_variables)
        except TypeError:
            # variables should be a dict-like object
            raise TypeError('Check syntax of variables.')

    t = template_engine(template)
    rendered = t.render(**variables).lstrip()

    # Try to detect if jinja2 is used
    module = template_engine.__module__
    if module is not None and 'jinja2.' in module:
        # Jinja2 might remove last newline
        if dry_text[-1] == '\n' and rendered[-1] != '\n':
            rendered += '\n'

    return rendered


def scriptdir():
    return os.path.split(os.path.realpath(__file__))[0]


def inputfiledir(filename):
    """Returns the directory where the given inputfile is located."""
    originalpath = os.path.abspath(os.path.join(os.getcwd(), filename))
    originaldir = os.path.split(originalpath)[0]
    return originaldir


def main():
    from docopt import docopt
    arguments = docopt(__doc__, argv=sys.argv[1:],
                       help=True, version=__version__)

    encoding = arguments['--encoding']
    if encoding is None:
        encoding = default_encoding

    filename = arguments['<filename>']
    if filename is not None:
        try:
            text = read_file(filename)
        except IOError as e:
            print('Could not open file. %s' % e)
            sys.exit(1)
    else:
        text = sys.stdin.read()

    # Set the engines
    name = 'yaml' if ('yaml' in variable_engines) else 'example'
    variable_engine_info = variable_engines[name]
    variable_engine, variable_engine_except = variable_engine_info

    name = 'jinja2' if ('jinja2' in template_engines) else 'example'
    template_engine_info = template_engines[name]
    template_engine, template_engine_except = template_engine_info

    if name == 'jinja2':
        # Add filevars() function for jinja2 templates
        if filename is None:
            originaldir = os.getcwd()
        else:
            originaldir = inputfiledir(filename)

        filevars = lambda path: variables_from_file(path, originaldir,
                                                    variable_engine,
                                                    encoding=encoding)
        template_variables['filevars'] = filevars

    try:
        rendered_text = render_dry_text(text, variable_engine, template_engine,
                                        add_variables=template_variables)
    except variable_engine_except as e:
        print('Error parsing variables: %s' % str(e).capitalize())
        sys.exit(1)
    except template_engine_except as e:
        print('Error parsing template: %s' % str(e).capitalize())
        sys.exit(1)

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
            sys.stdout.write(rendered_text.encode(encoding))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Quit.')
