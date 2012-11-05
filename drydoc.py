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

# 'Constants'
default_encoding = 'utf-8'
section_separator = '\n...\n'

import sys
try:
    import yaml
except ImportError:
    print('You must have PyYAML installed!')
    print('See: http://pyyaml.org/wiki/PyYAML#DownloadandInstallation')
    sys.exit(1)

try:
    import jinja2
except ImportError:
    print('You must have Jinja2 installed!')
    print('See: http://jinja.pocoo.org/')
    sys.exit(1)


def parse_dry_doc(text, encoding):
    text = text.decode(encoding, errors='replace')
    text_parts = text.split(section_separator, 1)
    definitions = text_parts[0].strip()
    template = text_parts[1]

    if not len(definitions):
        return text

    definitions = yaml.load(definitions)

    t = jinja2.Template(template)
    rendered = t.render(**definitions).lstrip()
    if text[-1] == '\n' and rendered[-1] != '\n':
        rendered += '\n'

    rendered = rendered.encode(encoding)
    return rendered


def main():
    from docopt import docopt
    arguments = docopt(__doc__, argv=sys.argv[1:],
                       help=True, version=__version__)

    filename = arguments['<filename>']
    try:
        f = open(filename)
    except IOError, e:
        print('Could not open file. %s' % e)
        sys.exit(1)
    text = f.read()
    f.close()

    encoding = arguments['--encoding']
    if encoding is None:
        encoding = default_encoding
    try:
        rendered_text = parse_dry_doc(text, encoding=encoding)
    except LookupError, e:
        print(str(e).capitalize())
        sys.exit(1)
    except yaml.reader.ReaderError, e:
        print('Error parsing variables: %s' % str(e).capitalize())
        sys.exit(1)

    output = arguments['--output']
    if output is not None:
        try:
            f = open(output, 'w')
        except IOError, e:
            print('Could not open file. %s' % e)
            sys.exit(1)
        f.write(rendered_text)
        f.close()
    else:
        print(rendered_text)


if __name__ == '__main__':
    main()
