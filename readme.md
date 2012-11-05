drydoc.py
---------

Program that renders DRY documents to actual text.

Dependencies:

- Python >=2.7, tested with 2.7 and 3.3
- Jinja2 http://jinja.pocoo.org/docs/
- PyYAML http://pyyaml.org/wiki/PyYAML

Usage
-----

    Usage:
      drydoc.py [<filename>] [--encoding=<encoding>] [--output=<output>]
      drydoc.py -h | --help
      drydoc.py --version


    Options:
      -h --help                 Show this screen.
      -v --version              Show version.
      -e --encoding=<encoding>  Encoding of the input file.
      -o --output=<output>      Output file.

What is DRY document?
---------------------

DRY document is a text file with variables and templating features to prevent you from
repeating yourself throughout the document.


Document structure
------------------

    ---
    variable: variables
    ...
    The actual template with {{ variable }}.


Document starts with variable definitions. Three empty dots in one line ends the variable definitions.
Variable definitions are in YAML http://en.wikipedia.org/wiki/YAML.
Variables must be in dictionary-like format, so they can be passed to template engine.

The rest of the document, after the three dots, is rendered as a Jinja2
template, with the variables defined in the beginning.
Whitespace from the beginning of actual template is stripped out.

Example
-------

DRY document:

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
    Documents support unicode, so you can have text like this '{{ unicode }}'.

Will render to:

    This is an example DRY document.

    Remember to buy:
        - milk
        - bread
        - cola

    Documents support unicode, so you can have text like this '汉语漢'.

Variables across files
----------------------

You can access variables in other DRY documents with filevars() function inside Jinja2 template.
Filepaths are always relative to the *original* DRY document.

For example:

/home/jack/drydoc1.txt:

    name: drydoc1.txt
    ...
    This document is '{{ name }}'.

    The other document is '{{ filevars('library/drydoc2.txt').name }}'.


/home/jack/library/drydoc2.txt:

    name: drydoc2.txt
    ...
    This document is '{{ name }}'.

    The other document is '{{ filevars('../drydoc1.txt').name }}'

The first level of dictionary nesting can be accessed via attribute, i.e. dict.attr. If the dictionary contains subdictionarys, they must be accessed normally with dict['attr'].

    filevars('dates.txt').weekdays['monday']

