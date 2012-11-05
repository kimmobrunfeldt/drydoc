This program renders documents with variables.

DRY document structure
----------------------

Three empty dots in one line ends the variable definitions.
Variable definitions are in YAML http://en.wikipedia.org/wiki/YAML.

The rest of the document, after the three dots, is rendered as a jinja2
template, with the variables defined in the beginning.
Whitespace from the beginning is stripped out.

Jinja2 documents are located in http://jinja.pocoo.org/docs/.

