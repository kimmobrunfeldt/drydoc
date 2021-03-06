
template_functions: templatefunctions.py
program_name: drydoc.py
separator: ...

...

General
=======

DRY document is a text file with variables and templating features to prevent you from
repeating yourself throughout the document. This document was also rendered with *{{program_name }}*.
This document is located in *example* directory.

*{{ program_name }}* renders DRY documents to actual text. You can structure your text files better.

Dependencies:

- Python >=2.7, tested with 2.7 and 3.3
- Jinja2 http://jinja.pocoo.org/docs/
- PyYAML http://pyyaml.org/wiki/PyYAML

If Jinja2 or PyYAML is not provided, documents are parsed with parsers in *parsers.py*.
They are just for an example how to add custom engines.

Usage
-----
{# This prints the help and intends it with 4 spaces #}
{{ system('python ../drydoc.py -h') | indent(4, true) }}

Writing DRY documents
=====================

{{ include('what_is_drydoc.txt') }}

Functions
=========

Python functions can be run in templates. In Jinja2 you must explicity add functions to the environment.
Custom functions that are usable in templates are defined in *{{ template_functions }}*.

**The working directory in functions should be the same as the document's location. For example, all file paths in a document are relative to the document itself.**

{{ include('functions.txt') }}

Thanks
------

- https://github.com/docopt/docopt
- http://jinja.pocoo.org/
- http://pyyaml.org/wiki/PyYAML
