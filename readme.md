drydoc.py
---------

It is a program that renders DRY documents to actual text

Dependencies

- Jinja2 http://jinja.pocoo.org/docs/
- PyYAML http://pyyaml.org/wiki/PyYAML

DRY document
-------------

DRY document is a text file with variables and templating features to prevent you from
repeating yourself throughout the document.


DRY document structure
----------------------

    ---
    variable: variables
    ...
    The actual template with {{ variable }}.


Document starts with variable definitions. Three empty dots in one line ends the variable definitions.
Variable definitions are in YAML http://en.wikipedia.org/wiki/YAML.

The rest of the document, after the three dots, is rendered as a Jinja2
template, with the variables defined in the beginning.
Whitespace from the beginning of actual template is stripped out.

Another example
---------------

    ---
    intro: This is an example DRY document.
    shopping_list:
        - milk
        - bread
        - cola
    unicode: 汉语漢
    ...

    {{ intro }}

    Remember to buy:
    {% for item in shopping_list %}    - {{ item }}
    {% endfor %}
    DRY documents support unicode, so you can have text like this '{{ unicode }}'.

Usage
-----

    Usage:
      drydoc.py <filename> [--encoding=<encoding>] [--output=<output>]
      drydoc.py -h | --help
      drydoc.py --version


    Options:
      -h --help                 Show this screen.
      -v --version              Show version.
      -e --encoding=<encoding>  Encoding of the input file.
      -o --output=<output>      Output file.