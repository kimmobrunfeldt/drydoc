General
=======

Program that renders DRY documents to actual text. You can structure your text files better.

Dependencies:

- Python >=2.7, tested with 2.7 and 3.3
- Jinja2 http://jinja.pocoo.org/docs/
- PyYAML http://pyyaml.org/wiki/PyYAML

If Jinja2 or PyYAML is not provided, documents are parsed with parsers in *parsers.py*.
They are just for an example how to add custom engines.

Usage
-----

    Renders DRY documents.
    
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
=====================

DRY document is a text file with variables and templating features to prevent you from
repeating yourself throughout the document. This document was also rendered with *drydoc.py*.
This document is located in *example* directory.

Document structure
------------------

    ---
    variable: variables
    ...
    The actual template with {{ variable }}.

Document starts with variable definitions. Definitions are followed by '...' in its own line end the section.
Variable definitions are in YAML http://en.wikipedia.org/wiki/YAML.
Variables must be in dictionary-like format, so they can be passed to template engine.

The rest of the document, after the three dots, is rendered as a Jinja2
template, with the variables defined in the beginning.
New lines from the beginning of actual template are stripped out.

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
    specialchars: 汉语漢
    ...
    
    {{ intro }}
    
    Remember to buy:
    {% for item in shopping_list %}    - {{ item }}
    {% endfor %}
    Documents support unicode, so you can have text like this '{{ specialchars }}'.

Will render to:

    This is an example DRY document.
    
    Remember to buy:
        - milk
        - bread
        - cola
    
    Documents support unicode, so you can have text like this '汉语漢'.

Functions
=========

Python functions can be run in templates. In Jinja2 you must explicity add functions to the environment.
Custom functions that are usable in templates are defined in *templatefunctions.py*.

filevars() - Variables across files
-----------------------------------

```python
def filevars(path):
    """Returns variables, from DRY doc located in path, in dict format."""
```

You can access variables in other DRY documents with filevars() function inside Jinja2 template.
Filepaths are always relative to the document.

For example:

*example/snippets/drydoc1.txt:*

    name: drydoc1.txt
    ...
    This document is '{{ name }}'.
    
    The other document is '{{ filevars('path/drydoc2.txt').name }}'.

*example/snippets/path/drydoc2.txt:*

    name: drydoc2.txt
    ...
    This document is '{{ name }}'.
    
    The other document is '{{ filevars('../drydoc1.txt').name }}'

You can access dictionary's keys via attribute: dict.attr, or with normal syntax: dict['attr'].

include() - Including documents
-------------------------------

```python
def include(path, render=True):
    """Returns another document located in path. Set render=False if
    you don't want to render the document.
    """
```

Documents can be included to other documents with include() function. When document B is included from document A, document B is rendered inside document A. Including document itself results to inifite recursion loop and will fail to exception.

*list.txt:*

    ---
    soda_list: [pepsi, cola, fanta]
    ...
    {% for item in soda_list %}{{ item }}
    {% endfor %}

*likes.txt:*

    ...
    I like:
    {{ include('list.txt') }}

Now when *likes.txt* is rendered, it produces:

    I like:
    pepsi
    cola
    fanta

You can also include normal text documents, just make sure they don't include the string which separates variable and template sections.
Normal text document must not contain a line with only '...' characters and it must not start with '...'

system() - Executing external programs
--------------------------------------

```python
def system(cmd):
    """Executes cmd in shell and returns its output."""
```

You can execute shell commands and pipe their output to the document with system() function.

For example, a DRY document which renders to output of *'ls -l'*

    ...
    {{ system('ls -l') }}

Dynamically get newest trends from Twitter in nicely formatted JSON:

    ...
    {{ system('curl -s http://api.twitter.com/1/trends/1.json | python -m json.tool') }}
