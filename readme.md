This program parses DRY documents.

Usage:
  drydoc.py <filename> [--encoding=<encoding>] [--output=<output>]
  drydoc.py -h | --help
  drydoc.py --version


Options:
  -h --help                 Show this screen.
  -v --version              Show version.
  -e --encoding=<encoding>  Encoding of the input file.
  -o --output=<output>      Output file.

DRY document structure
----------------------

    variable: variables
    ...
    The actual template with {{ variable }}.


Document starts with variable definitions. Three empty dots in one line ends the variable definitions.
Variable definitions are in YAML http://en.wikipedia.org/wiki/YAML.

The rest of the document, after the three dots, is rendered as a jinja2
template, with the variables defined in the beginning.
Whitespace from the beginning is stripped out.

Jinja2 documentation: http://jinja.pocoo.org/docs/.

