drydoc.py
---------

Program that renders DRY documents to actual text.

Dependencies:

- Python >=2.7, tested with 2.7 and 3.3
- Jinja2 http://jinja.pocoo.org/docs/
- PyYAML http://pyyaml.org/wiki/PyYAML

If Jinja2 or PyYAML is not provided, documents are parsed with parsers in *parsers.py*.
They are just for an example how to add custom engines.

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


Document starts with variable definitions. '...' in its own line ends the variable definitions.
Variable definitions are in YAML http://en.wikipedia.org/wiki/YAML.
Variables must be in dictionary-like format, so they can be passed to template engine.

The rest of the document, after the three dots, is rendered as a Jinja2
template, with the variables defined in the beginning.
Whitespace from the beginning of actual template is stripped out.

If there are no variable definitions, document must contain '...' in it, for it to be recognized as a DRY document.
Rendering a document without '...' separator produces the document itself.

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

*/home/jack/drydoc1.txt:*

    name: drydoc1.txt
    ...
    This document is '{{ name }}'.

    The other document is '{{ filevars('library/drydoc2.txt').name }}'.


*/home/jack/library/drydoc2.txt:*

    name: drydoc2.txt
    ...
    This document is '{{ name }}'.

    The other document is '{{ filevars('../drydoc1.txt').name }}'

The first level of dictionary nesting can be accessed via attribute, i.e. dict.attr. If the dictionary contains subdictionarys, they must be accessed normally with dict['attr'].

    {{ filevars('dates.txt').weekdays['monday'] }}

Including documents
-------------------

Documents can be included to other documents with include() function. When document B is included from document A, document B is rendered inside document A. Including document itself results to inifite recursion loop and will fail to exception.

*list.txt:*

    ---
    soda_list: [pepsi, cola, fanta]
    ...
    {% for item in soda_list %}{{ item }}
    {% endfor %}

*doc.txt:*

    ...
    I like:
    {{ include('list.txt') }}

Now when *doc.txt* is rendered, it produces:

    I like:
    pepsi
    cola
    fanta

You can also include normal text documents, just make sure they don't include the string which separates variable and template sections.
Normal text document must not contain a line with only '...' characters and it must not start with '...'
