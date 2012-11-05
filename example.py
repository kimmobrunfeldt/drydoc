#!/usr/bin/python

"""Parses DRY-documents.

Usage:
  drydoc.py <filename> [--encoding=<encoding>] [--output=<output>]
  drydoc.py -h | --help
  drydoc.py --version


Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  -e --encoding=<encoding>  Encoding of the input file.
  -o --output=<output>      Output file.
"""

__version__ = '0.0.1'


import sys
import parsers

_PY3 = sys.version_info >= (3, 0)

# 'Constants'
default_encoding = 'utf-8'
section_separator = '\n...\n'

# Callable that parses variables and returns a dict
variable_engine = parsers.parse_variables
# What exceptions to catch gracefully, if you want to provide better error
# messages, make your own exception class and format the errors in it.
variable_engine_except = (ValueError)

# Template engine is a class which constructor takes the template. It must
# support .render(), which takes variables as keyword arguments.
template_engine = parsers.Template
template_engine_name = 'custom'
template_engine_except = ()


def read_file(filepath, encoding=default_encoding):
    if _PY3:
        global open
        open = lambda f, mode: open(f, mode, encoding=encoding)

    with open(filepath, 'r') as f:
        content = f.read()

    if not _PY3:
        content = content.decode(encoding)

    return content


def write_file(text, filepath, encoding=default_encoding):
    if _PY3:
        global open
        open = lambda f, mode: open(f, mode, encoding=encoding)
    else:
        text = text.encode(encoding)

    with open(filepath, 'w') as f:
        f.write(text)


def render_dry_text(dry_text, variable_engine=variable_engine,
                    template_engine=template_engine):
    """Returns rendered text from DRY text. dry_text must be unicode."""
    text_parts = dry_text.split(section_separator, 1)
    variables = text_parts[0].strip()
    template = text_parts[1]

    if not len(variables):
        return dry_text

    variables = variable_engine(variables)

    t = template_engine(template)
    rendered = t.render(**variables).lstrip()

    if template_engine_name == 'jinja2':
        # Jinja2 might remove last newline
        if dry_text[-1] == '\n' and rendered[-1] != '\n':
            rendered += '\n'

    return rendered


def main():
    from docopt import docopt
    arguments = docopt(__doc__, argv=sys.argv[1:],
                       help=True, version=__version__)

    encoding = arguments['--encoding']
    if encoding is None:
        encoding = default_encoding

    text = parsers.example_doc

    try:
        rendered_text = render_dry_text(text)
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
        print(rendered_text.encode(encoding))


if __name__ == '__main__':
    main()
